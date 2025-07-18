# Python useful libraries
import math
import numpy as np
import pandas as pd
from multiprocessing.pool import ThreadPool
from multiprocessing import pool
from collections import Counter

# Own functions
from . import stringfunctions
from . import plotfunctions

# For metrics calculation (classification and regression)
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score, confusion_matrix, precision_recall_fscore_support, accuracy_score

# Pyspark classification and regression Models
from pyspark.ml.regression import DecisionTreeRegressor, RandomForestRegressor, GBTRegressor
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, GBTClassifier, NaiveBayes, LinearSVC

# Pyspark Evaluator
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator, RegressionEvaluator

# Grid builder and cross validation
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder, _parallelFitTasks, CrossValidatorModel

# Pyspark rand
from pyspark.sql.functions import rand

# plot
import matplotlib.pyplot as plt
import seaborn as sn

# clasificación basada en https://spark.apache.org/docs/2.2.0/mllib-evaluation-metrics.html#binary-classification y en
# https://towardsdatascience.com/machine-learning-with-pyspark-and-mllib-solving-a-binary-classification-problem-96396065d2aa (binaria)

"""
Modification of CrossValidator class of pyspark official sourcecode. Class that manages supervised learning cross validation. Fit function of the class has been modified 

source of the original class: https://spark.apache.org/docs/latest/api/python/_modules/pyspark/ml/tuning.html#CrossValidator

"""
class CrossValidatorBestModelTraining(CrossValidator):
    
    # Just included, not modified
    def _kFold(self, dataset):
        nFolds = self.getOrDefault(self.numFolds)
        foldCol = False # Changed to False

        datasets = []
        if not foldCol:
            # Do random k-fold split.
            seed = self.getOrDefault(self.seed)
            h = 1.0 / nFolds
            randCol = self.uid + "_rand"
            df = dataset.select("*", rand(seed).alias(randCol))
            for i in range(nFolds):
                validateLB = i * h
                validateUB = (i + 1) * h
                condition = (df[randCol] >= validateLB) & (df[randCol] < validateUB)
                validation = df.filter(condition)
                train = df.filter(~condition)
                datasets.append((train, validation))
        else:
            # Use user-specified fold numbers.
            def checker(foldNum):
                if foldNum < 0 or foldNum >= nFolds:
                    raise ValueError(
                        "Fold number must be in range [0, %s), but got %s." % (nFolds, foldNum))
                return True

            checker_udf = UserDefinedFunction(checker, BooleanType())
            for i in range(nFolds):
                training = dataset.filter(checker_udf(dataset[foldCol]) & (col(foldCol) != lit(i)))
                validation = dataset.filter(
                    checker_udf(dataset[foldCol]) & (col(foldCol) == lit(i)))
                if training.rdd.getNumPartitions() == 0 or len(training.take(1)) == 0:
                    raise ValueError("The training data at fold %s is empty." % i)
                if validation.rdd.getNumPartitions() == 0 or len(validation.take(1)) == 0:
                    raise ValueError("The validation data at fold %s is empty." % i)
                datasets.append((training, validation))

        return datasets

    """
    Function that manages the training of pyspark supervised learning algorithms. Modified to get the best model obtained in cross validation process and its metrics.

    Parameters:

    self: context
    dataset: dataset with all available data. Split in test/train will be done in this function.

    Return: tuple with the original return, the cross validator model (in this case the best model that has been found) and 4 extra variables:
     - metrics2 - values of the metric used for comparison (f1Score, AUC, RMSE... info in pyspark evaluators
     https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.evaluation.BinaryClassificationEvaluator.html)
     - bestTrainingModel_train - Train set used in the training of the best model
     - bestTrainingModel_test - Test set used in the training of the best model
     - bestIndex2 - Index of the best model found during the cross validation run 

    """
    def _fit(self, dataset):
        est = self.getOrDefault(self.estimator)
        epm = self.getOrDefault(self.estimatorParamMaps)
        numModels = len(epm)
        eva = self.getOrDefault(self.evaluator)
        nFolds = self.getOrDefault(self.numFolds)
        metrics = [0.0] * numModels
        
        # Added - metrics of each fold
        metrics2 = [0.0] * nFolds

        pool = ThreadPool(processes=min(self.getParallelism(), numModels))
        subModels = None
        collectSubModelsParam = self.getCollectSubModels()
        if collectSubModelsParam:
            subModels = [[None for j in range(numModels)] for i in range(nFolds)]

        datasets = self._kFold(dataset)
        for i in range(nFolds):
            validation = datasets[i][1].cache()
            train = datasets[i][0].cache()

            tasks = _parallelFitTasks(est, train, eva, validation, epm, collectSubModelsParam)
            for j, metric, subModel in pool.imap_unordered(lambda f: f(), tasks):
                metrics[j] += (metric / nFolds)
                
                # Added - store the metric obtained by each model
                metrics2[i] += metric
                if collectSubModelsParam:
                    subModels[i][j] = subModel

            validation.unpersist()
            train.unpersist()

        if eva.isLargerBetter():
            bestIndex = np.argmax(metrics)
            
            # Added - get the best fold
            bestIndex2 = np.argmax(metrics2)
        else:
            bestIndex = np.argmin(metrics)
            
            # Added - get the best fold
            bestIndex2 = np.argmin(metrics2)
        
        # Added - get test and training datasets used during the training of the best model found in cross validation process
        bestTrainingModel_train = datasets[bestIndex2][0]
        bestTrainingModel_test = datasets[bestIndex2][1]
        
        # Modified - bestModel is now the best model found during the cross validation
        bestModel = est.fit(bestTrainingModel_train, epm[bestIndex])
        
        return self._copyValues(CrossValidatorModel(bestModel, metrics, subModels)), metrics2, bestTrainingModel_train, bestTrainingModel_test, bestIndex2
    
"""
Function that gets the plot of the ROC curve considering both labels (0 and 1) as positive (2 plots). Only used in binary classification and probabilistic classifiers.
Information about it: Provost, F., Domingos, P.Well-trained PETs: Improving probability estimation trees, CeDER Working Paper.

Parameters:

probability_0_param: list of probabilities if 0 is the positive label (they build the ROC curve and some binary classifiers can be considered as probabilistic)
probability_1_param: list of probabilities if 1 is the positive label 
labels_param: list with labels predicted by the best bodel found in the cross validation
labelMapping: dictionary with mapping that the system did with labels

Return: dictionary with two fields:
 - rocImage0: ROC curve considering 0 as the positive label of the binary classification problem
 - rocImage1: ROC curve considering 1 as the positive label of the binary classification problem

"""
def get_roc_curve(probability_0_param, probability_1_param, labels_param, labelMapping):
    
    # dictionary that contains the images. Name matches with the model result.
    roc_images_dict = {}
        
    # get title of the plots
    title_0 = "ROC curve with positive class 0 - '" + str(labelMapping[0]) + "'"
    title_1 = "ROC curve with positive class 1 - '" + str(labelMapping[1]) + "'"
    
    # get the roc curve where the label 0 is the positive case POSITIVE-NEGATIVE
    roc_images_dict["rocImage0"] = get_roc_curve_image(probability_0_param, labels_param.count(0), labels_param.count(1), labels_param, 0, title_0)
    # get the roc curve where the label 1 is the positive case POSITIVE-NEGATIVE
    roc_images_dict["rocImage1"] = get_roc_curve_image(probability_1_param, labels_param.count(1), labels_param.count(0), labels_param, 1, title_1)
    
    return roc_images_dict

"""
Function that gets the plot of 1 ROC curve. Only used in binary classification and probabilistic classifiers.

Parameters:

prob_param: list of probabilities if positive_class_param is the positive label 
P: count of positive instances
N: count of negative instances
positive_class_param: integer with the positive classification value (1 or 0)
labels_param: list with labels predicted by the best bodel found in the cross validation
title_param: string with the title that the ROC curve plot will have

Return: ROC_image: string with png image
"""
def get_roc_curve_image(prob_param, P, N, labels_param, positive_class_param, title_param):
    
    # sorted list
    prob = prob_param.copy()
    prob.sort(reverse=True)
    
    # initialize the rest of parameters
    FP = 0
    TP = 0
    R = []
    f_prev = -1
    
    # for every instance O(n)
    for i in range(len(prob)):
        
        # update previous score value
        if (f_prev != prob[i]):
            R.append([ FP/N, TP/P ])
            f_prev = prob[i]
        
        # update TP and FP values
        if (labels_param[i] == positive_class_param):
            TP += 1
        else:
            FP += 1
    
    # append last value of the ROC curve
    R.append([1,1])
    
    # get the FPR and TPR
    FPR = []
    TPR = []
    for elem in R:
        FPR.append(elem[0])
        TPR.append(elem[1])
    
    # Build the plot and get the image
    ROC_image = plotfunctions.plot_ml("rocCurve", {"title": title_param, "FPR": FPR, "TPR":TPR, "probabilities": prob})
    
    return ROC_image

"""
Function that gets the rates that can be obtained from actual labels and predictions, from the confusion matrix of a binary classification problem.

Parameters:

predictions: list of predictions done by the binary classification model
labels: list of actual labels of the test set
positive_class_label: integer with the positive classification value (1 or 0)
negative_class_label: integer with the negative classification value (1 or 0)

Return: rates_dict: dictionary with the rates, contained in 5 fields:
 - precisionBest: Precision obtained by the model
 - recallBest: Recall obtained by the model
 - fprBest: False positives ratio obtained by the model
 - tnrBest: True negatives ratio obtained by the model
 - f1Score: F1 Score obtained by the model
"""
def get_rates(predictions, labels, positive_class_label, negative_class_label):
    
    # dictionary that will contain all rates. Names of the dictionary variables are set to match with model's variables name
    rates_dict = {}
    
    # all rates
    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for i in range(len(predictions)): 
        if labels[i]==predictions[i]==positive_class_label:
            TP += 1
        if predictions[i]==positive_class_label and labels[i]!=predictions[i]:
            FP += 1
        if labels[i]==predictions[i]==negative_class_label:
            TN += 1
        if predictions[i]==negative_class_label and labels[i]!=predictions[i]:
            FN += 1

    # precision
    if (TP > 0):
        rates_dict["precisionBest"+str(positive_class_label)] = TP/(TP+FP)
    else:
        rates_dict["precisionBest"+str(positive_class_label)] = 0
    
    # recall or sensitivity or TP Rate 0.5 threshold (from confusion matrix)
    rates_dict["recallBest"+str(positive_class_label)] = TP/labels.count(positive_class_label)
    
    # FP Rate 0.5 threshold (from confusion matrix)
    rates_dict["fprBest"+str(positive_class_label)] = FP/labels.count(negative_class_label)
    
    # TN Rate or specificity
    rates_dict["tnrBest"+str(positive_class_label)] = 1-rates_dict["fprBest"+str(positive_class_label)]
    
    # F1 measure or F1 Score
    rates_dict["f1Score"+str(positive_class_label)] = TP/(TP+1/2*(FP+FN))
                                     
    return rates_dict

"""
Function that gets all the measures and information that can be obtained from actual labels and predictions. Used in binary classification problem.

Parameters:

predictions: list of predictions done by the binary classification model
labels: list of actual labels of the test set

Return: measures_dict: dictionary with the rates from the confusion matrix (function get_rates) and three extra measures, contained in 3 fields:
 - accuracyBest: Accuracy obtained by the model
 - cmBest: Confusion matrix obtained by the model (string png format)
 - cmNormBest: Normalized confusion matrix obtained by the model (string png format)
"""
def get_measures(predictions, labels):
    
    # dictionary that will contain all measures. Names of the dictionary variables are set to match with model's variables name
    measures_dict = {}
    
    # accuracy
    measures_dict["accuracyBest"] = sum(1 for x,y in zip(predictions,labels) if x == y) / len(predictions)
    
    # confusion matrix
    measures_dict["cmBest"] = plotfunctions.plot_ml("confusionMatrix", {"data": confusion_matrix(labels, predictions), "xlabel": "Predictions", "ylabel": "Labels"})
    
    # normalized confusion matrix
    measures_dict["cmNormBest"] = plotfunctions.plot_ml("confusionMatrix", {"data": confusion_matrix(labels, predictions, normalize='pred'),
                                                                            "xlabel": "Predictions", "ylabel": "Labels"})

    # all rates, precision, recall, FPR, TNR, F1 score, measures from cm
    
    # with 0 as positive class
    rates_dict_0 = get_rates(predictions, labels, 0, 1)
    
    # with 1 as positive class
    rates_dict_1 = get_rates(predictions, labels, 1, 0)
    
    # Update return dictionary with all the needed values
    measures_dict.update(rates_dict_0)
    measures_dict.update(rates_dict_1)
    
    return measures_dict
    

"""
############################ Binary Logistic Regression ############################

Function that runs a cross validation based on binary logistic regression, a binary classification algorithm. It uses pyspark and returns all the measures founded in the CV.

Parameters:

df: preprocessed pyspark dataframe with labels and input data
maxIter_param: Parameter of pyspark the logistic regression model/algorithm
parallelism_param: Parameter of pyspark cross validation
n_folds_param: Parameter of pyspark cross validation. Number of folds.

Return: binarylog_classification_results_dict: Dictionary with the most important measures. They will be part of the result instance that will be inserted in database:
- aucMean - Mean of the area under curve of all models found in CV
- aucBest - Best area under curve value found among all models of CV
- accuracyBest - Best accuracy value found among all models of CV
- coeffImage - Plot with the Beta coefficients of the binary logistic regression
- rocImage - ROC curve plot of the best model
- prImage - Precision-Recall plot of the best model
"""
def binary_log_regression_classifier_cv(df, maxIter_param, parallelism_param, n_folds_param):
    
    # Create the Logistic Regresion model and indicate the relevant columns
    lr = LogisticRegression(featuresCol = 'features', labelCol = 'label')
    
    # Create the grid with the parameters that are going to be tested
    grid = ParamGridBuilder().addGrid(lr.maxIter, [maxIter_param]).build()
    
    # Create evaluator (Binary classification default evaluator, using numBins = 1000 and metric AUC)
    evaluator = BinaryClassificationEvaluator()
    
    # Create the cross validator using the estimator, the grid, the evaluator and the selected number of cores and folds 
    cv = CrossValidator(estimator=lr, estimatorParamMaps=grid, evaluator=evaluator, parallelism=parallelism_param, numFolds = n_folds_param)
    
    # Fit the CV
    cvModel = cv.fit(df)
    
    ######### Get the most relevant results #########
    
    # things that we have to keep in a binary LRM: beta coefficients, AUC, ROC curve (FPR vs TPR)-ver de donde los coge (supongo que del threshold luce que sí porque en scala lo usa así), precision-recall curve y accuracy
        
    # create an empty dictionary that will contain the results of the algorithm execution. . Names of the dictionary variables are set to match with result model's variables name
    binarylog_classification_results_dict = {}

    # average AUC of each validation set of each fold, not training set
    binarylog_classification_results_dict["aucMean"] = cvModel.avgMetrics[0]
    
    # get the summary of the best found model
    trainingSummary = cvModel.bestModel.summary
    
    # coefficients of the best linear regression model
    coeff = cvModel.bestModel.coefficients
    
    # Best training model AUC
    binarylog_classification_results_dict["aucBest"] = trainingSummary.areaUnderROC
    
    # Best training model Accuracy
    binarylog_classification_results_dict["accuracyBest"] = trainingSummary.accuracy
    
    # Best training model ROC curve
    ROC_best = trainingSummary.roc
    
    # Best training model PR (precision-recall)
    PR_best = trainingSummary.pr
    
    # get the images
    
    # coefficients
    coeff_sort = np.sort(coeff)
    
    binarylog_classification_results_dict["coeffImage"] = plotfunctions.plot_ml("standardPlot", {"data": coeff_sort,
                                                                                                 "title": "Model's Beta coefficients (sorted)",
                                                                                                 "xlabel": "coeff number", "ylabel": "Beta Coefficients"})
    
    # ROC curve
    ROC_pd = ROC_best.toPandas()

    binarylog_classification_results_dict["rocImage"] = plotfunctions.plot_ml("standardPlot", {"data": ROC_pd['FPR'], "data2": ROC_pd['TPR'],
                                           "title": "ROC Curve", "xlabel": "False Positive Rate", "ylabel": "True Positive Rate"})
    
    # Precision-Recall curve
    PR_pd = PR_best.toPandas()
    
    binarylog_classification_results_dict["prImage"] = plotfunctions.plot_ml("standardPlot", {"data": PR_pd['recall'], "data2": PR_pd['precision'],
                                           "title": "PR Curve", "xlabel": "recall", "ylabel": "precision"})
    
    return binarylog_classification_results_dict

"""
############################ Multinomial Logistic Regression ############################

Function that runs a cross validation based on multiclass logistic regression, a multiclass classification algorithm. It uses pyspark and returns all the measures founded in the CV.

Parameters:

df: preprocessed pyspark dataframe with labels and input data
maxIter_param: Parameter of pyspark the logistic regression model/algorithm
parallelism_param: Parameter of pyspark cross validation
n_folds_param: Parameter of pyspark cross validation. Number of folds.

Return: multiclasslog_classification_results_dict: Dictionary with the most important measures. They will be part of the result instance that will be inserted in database:
- f1Mean - Mean of the F1Score of all models found in CV
- accuracyBest - Best accuracy value found among all models of CV
- coeffMatrix - Matrix with the Beta coefficients (logisitc regression) of the best model found in CV of multiclass logistic regression
- f1ByLabel - F1Score value by label of the best model found in CV
- fprByLabel - FPR value by label of the best model found in CV
- tprByLabel - TPR value by label of the best model found in CV
- precisionByLabel - Precision value by label of the best model found in CV
- recallByLabel - Recall value by label of the best model found in CV
- f1Weighted - F1Score value weighted (computing a weighted mean from measures by label) of the best model found in CV
- fprWeighted - FPR value weighted (computing a weighted mean from measures by label) of the best model found in CV
- tprWeighted - TPR value weighted (computing a weighted mean from measures by label) of the best model found in CV
- precisionWeighted - Precision value weighted (computing a weighted mean from measures by label) of the best model found in CV
- recallWeighted - Recall value weighted (computing a weighted mean from measures by label) of the best model found in CV
"""
def multiclass_log_regression_classifier_cv(df, maxIter_param, parallelism_param, n_folds_param):
    # Create the Logistic Regresion model and indicate the relevant columns
    lr = LogisticRegression(featuresCol = 'features', labelCol = 'label')
    
    # Create the grid with the parameters that are going to be tested
    grid = ParamGridBuilder().addGrid(lr.maxIter, [maxIter_param]).build()
    
    # Create evaluator (Multiclass classification default evaluator, using default metric F1-Score and rest of default parameters: metricLabel=0.0, beta=1.0 and eps=1e-15)
    evaluator = MulticlassClassificationEvaluator()
    
    # Create the cross validator using the estimator, the grid, the evaluator and the selected number of cores and folds 
    cv = CrossValidator(estimator=lr, estimatorParamMaps=grid, evaluator=evaluator, parallelism=parallelism_param, numFolds = n_folds_param)
    
    # Fit the CV
    cvModel = cv.fit(df)
    
    ######### Get the most relevant results #########
    
    # things that we have to keep in a multiclass LRM: averahe metrics, matrix of coefficients, metrics per-label, accuracy and weighted  falsePositiveRate, truePositiveRate, fMeasure, precision, recall
    
    # create an empty dictionary that will contain the results of the algorithm execution. . Names of the dictionary variables are set to match with result model's variables name
    multiclasslog_classification_results_dict = {}

    # average F1 of each validation set of each fold, not training set
    multiclasslog_classification_results_dict["f1Mean"] = cvModel.avgMetrics[0]
    
    # coefficients matrix of the best linear regression model
    multiclasslog_classification_results_dict["coeffMatrix"] = cvModel.bestModel.coefficientMatrix
    
    # get the summary of the best founded model
    trainingSummary = cvModel.bestModel.summary
    
    # best training model accuracy
    multiclasslog_classification_results_dict["accuracyBest"] = trainingSummary.accuracy
    
    ## Best training model metrics by label ##

    # F1 Score by label
    F1_by_label = []
    for i, f in enumerate(trainingSummary.fMeasureByLabel()):
        F1_by_label.append([i,f])
    multiclasslog_classification_results_dict["f1ByLabel"] = str(F1_by_label)
    
    # False Positive Rate by label
    FPR_by_label = []
    for i, rate in enumerate(trainingSummary.falsePositiveRateByLabel):
        FPR_by_label.append([i,rate])
    multiclasslog_classification_results_dict["fprByLabel"] = str(FPR_by_label)
    
    # True Positive Rate by label
    TPR_by_label = []
    for i, rate in enumerate(trainingSummary.truePositiveRateByLabel):
        TPR_by_label.append([i,rate])
    multiclasslog_classification_results_dict["tprByLabel"] = str(TPR_by_label)
                                              
    # Precision by label
    precision_by_label = []
    for i, prec in enumerate(trainingSummary.precisionByLabel):
        precision_by_label.append([i,rate])
    multiclasslog_classification_results_dict["precisionByLabel"] = str(precision_by_label)
                                              
    # Recall by label
    recall_by_label = []
    for i, rec in enumerate(trainingSummary.recallByLabel):
        recall_by_label.append([i,rate])
    multiclasslog_classification_results_dict["recallByLabel"] = str(recall_by_label)
                                              
    ## Best training model Weighted measures ##
    
    # Weigthed F1 Score
    multiclasslog_classification_results_dict["f1Weighted"] = trainingSummary.weightedFMeasure()
    
    # Weigthed False Positive Rate
    multiclasslog_classification_results_dict["fprWeighted"] = trainingSummary.weightedFalsePositiveRate
    
    # Weigthed True Positive Rate
    multiclasslog_classification_results_dict["tprWeighted"] = trainingSummary.weightedTruePositiveRate
    
    # Weigthed Precision 
    multiclasslog_classification_results_dict["precisionWeighted"] = trainingSummary.weightedPrecision
    
    # Weigthed Recall
    multiclasslog_classification_results_dict["recallWeighted"] = trainingSummary.weightedRecall

    return multiclasslog_classification_results_dict

"""
Function that gets the correct classifier or regressor from pyspark library. It will get the classifier associated to the name received as parameter.

Parameters:

algorithm_name: string with the algorithm name.

Return: model associated to the algorithm received as parameter.
"""
def get_classifier_regressor_model(algorithm_name):
    
    if (algorithm_name == "BinaryDecisionTree" or algorithm_name == "MulticlassDecisionTree"):
                
        model = DecisionTreeClassifier
        
    elif (algorithm_name == "BinaryRandomForest" or algorithm_name == "MulticlassRandomForest"):
        
        model = RandomForestClassifier
        
    elif (algorithm_name == "BinaryGBT"):
        
        model = GBTClassifier
        
    elif (algorithm_name == "BinaryNaiveBayes" or algorithm_name == "MulticlassNaiveBayes"):
        
        model = NaiveBayes
        
    elif (algorithm_name == "BinaryLinearSVC"):
        
        model = LinearSVC
        
    elif (algorithm_name == "DecisionTreeRegression"):
                
        model = DecisionTreeRegressor
        
    elif (algorithm_name == "RandomForestRegression"):
        
        model = RandomForestRegressor
        
    elif (algorithm_name == "GBTRegression"):
        
        model = GBTRegressor
        
    return model

"""

Function that builds the pyspark estimator and grid, used in the cross validation model of classification and regression algorithms.

Parameters:

algorithm_name: string with the algorithm name.
algorithm_parameters: Dictionary with the algorithm parameters name and values. Name of the dict keys (alg parameters)
can be found in https://spark.apache.org/docs/latest/ml-classification-regression.html 

Return: Tuple with the built estimator and grid.
"""
# function for building the estimator and grid
def create_estimator_grid(algorithm_name, algorithm_parameters):
    
    # clean the dictionary and use only pyspark classifiers/regressors parameters (parallelism and numFolds are for cross validation)
    algorithm_parameters_clean = algorithm_parameters.copy()
    algorithm_parameters_clean.pop('parallelism', None)
    algorithm_parameters_clean.pop('numFolds', None)
    
    # get the correct model of classifier or regressor depending on selected algorithm
    model = get_classifier_regressor_model(algorithm_name)
    
    # build the estimator
    est = model(featuresCol = 'features', labelCol = 'label', **algorithm_parameters_clean)
    
     # Build the grid with all the parameters of the classifier/regressor that are going to be tested (stored in algorithm_parameters_clean dictionary)
    grid = ParamGridBuilder()

    # Add each parameter with its associated value to the grid
    for key, value in algorithm_parameters_clean.items():
        grid = grid.addGrid(eval("est."+key), [value])

    # build the grid
    grid = grid.build()
         
    return est, grid
    
"""
################################# REST OF BINARY CLASSIFIERS #################################

Function that runs a cross validation based on the binary classification algorithm received as a parameter. It uses pyspark and returns all the measures founded in the CV.

Parameters:

algorithm_name: string with the algorithm name.
preprocessed_dataframe: preprocessed pyspark dataframe with labels and input data
algorithm_parameters: Dictionary with the algorithm parameters name and values. Name of the dict keys (alg parameters)
can be found in https://spark.apache.org/docs/latest/ml-classification-regression.html 
labelMapping: dictionary with mapping that the system did with labels

Return: binary_classification_results_dict: Dictionary with the most important measures. They will be part of the result instance that will be inserted in database:
 - aucMean - Mean of the area under curve of all models found in CV
 - aucBest - Best area under curve value found among all models of CV
 - accuracyBest - Best accuracy value found among all models of CV
 - precisionBest: Precision obtained by the best model
 - recallBest: Recall obtained by the best model
 - fprBest: False positives ratio obtained by the best model
 - tnrBest: True negatives ratio obtained by the best model
 - f1Score: F1 Score obtained by the best model
 - cmBest: Confusion matrix obtained by the best model (string png format)
 - cmNormBest: Normalized confusion matrix obtained by the best model (string png format)
 - rocImage0: ROC curve considering 0 as the positive label of the binary classification problem
 - rocImage1: ROC curve considering 1 as the positive label of the binary classification problem
"""
def binary_classifiers(algorithm_name, preprocessed_dataframe, algorithm_parameters, labelMapping):
    
    # create the estimator and grid, depending on the algorithm
    est, grid = create_estimator_grid(algorithm_name, algorithm_parameters)
    
    # Create evaluator (Binary classification default evaluator, using numBins = 1000 and metric AUC)
    evaluator = BinaryClassificationEvaluator()
    
    # Create the cross validator using the estimator, the grid, the evaluator and the selected number of cores and folds 
    cv  = CrossValidatorBestModelTraining(estimator=est, estimatorParamMaps=grid, evaluator=evaluator,
                                          parallelism=algorithm_parameters["parallelism"], numFolds = algorithm_parameters["numFolds"])
    
    # Fit the CV
    cvModel, metrics, bestTrainingModel_train, bestTrainingModel_test, bestIndex2 = cv.fit(preprocessed_dataframe)
    
    #get the best model found in CV
    bestModel = cvModel.bestModel
    
    # Get the predictions and labels of the best training model found in CV
    predictions = bestModel.transform(bestTrainingModel_test)
    
    # get predictions, labels and probabilities as lists
    
    # change it to pandas df
    predictions_pandas = predictions.select("label", "prediction").toPandas()
    
    # get predictions and labels
    predictions_list = list(predictions_pandas["prediction"])
    labels_list = list(predictions_pandas["label"])
    
    ######### Get the most relevant results - binary classification #########
    
    # dictionary that will contain all relevant results. Names of the dictionary variables are set to match with result model's variables name
    binary_classification_results_dict = {}

    # average AUC of each validation set of each fold, not training set
    binary_classification_results_dict["aucMean"] = cvModel.avgMetrics[0]
    
    # Best training model AUC
    binary_classification_results_dict["aucBest"] = metrics[bestIndex2]
    
    # get the rest of measures: - Obtain the measures associated to the model with the best AUC value, best model found in CV
    measures_dict = get_measures(predictions_list, labels_list)
    
    # update the output dictionary
    binary_classification_results_dict.update(measures_dict)
    
    # get the roc curve in case it is a probabilistic classifier or a discrete one with probabilities
    if (algorithm_name != "BinaryGBT" and algorithm_name != "BinaryLinearSVC"):
    
        predictions_pandas["probability"] = predictions.select("probability").toPandas()['probability']
    
        # initialize and get the lists from pandas elements
        prob_0_list = []
        prob_1_list = []

        for elem in predictions_pandas["probability"]:
            prob_0_list.append(elem[0])
            prob_1_list.append(elem[1])
                    
        # get manually the roc curve using the algorithm of the article https://people.inf.elte.hu/kiss/13dwhdm/roc.pdf
        roc_images_dict = get_roc_curve(prob_0_list, prob_1_list, labels_list, labelMapping)
        
        # update the output dictionary
        binary_classification_results_dict.update(roc_images_dict)
        
    return binary_classification_results_dict

"""
################################# REST OF MULTICLASS CLASSIFIERS #################################

Function that runs a cross validation based on the multiclass classification algorithm received as a parameter. It uses pyspark and returns all the measures founded in the CV.

Parameters:

algorithm_name: string with the algorithm name.
preprocessed_dataframe: preprocessed pyspark dataframe with labels and input data
algorithm_parameters: Dictionary with the algorithm parameters name and values. Name of the dict keys (alg parameters)
can be found in https://spark.apache.org/docs/latest/ml-classification-regression.html 

Return: multiclass_classification_results_dict: Dictionary with the most important measures. They will be part of the result instance that will be inserted in database:
 - F1Mean - Mean of the F1 Score of all models found in CV
 - accuracyBest - Best accuracy value found among all models of CV
 - cmBest: Confusion matrix obtained by the best model (string png format)
 - cmNormBest: Normalized confusion matrix obtained by the best model (string png format)
 - f1ByLabel - F1Score value by label of the best model found in CV
 - fprByLabel - FPR value by label of the best model found in CV
 - tnrByLabel - TNR value by label of the best model found in CV
 - precisionByLabel - Precision value by label of the best model found in CV
 - recallByLabel - Recall value by label of the best model found in CV
 - f1Weighted - F1Score value weighted (computing a weighted mean from measures by label) of the best model found in CV
 - fprWeighted - FPR value weighted (computing a weighted mean from measures by label) of the best model found in CV
 - tnrWeighted - TNR value weighted (computing a weighted mean from measures by label) of the best model found in CV
 - precisionWeighted - Precision value weighted (computing a weighted mean from measures by label) of the best model found in CV
 - recallWeighted - Recall value weighted (computing a weighted mean from measures by label) of the best model found in CV
"""
def multiclass_classifiers(algorithm_name, preprocessed_dataframe, algorithm_parameters):

     # create the estimator and grid, depending on the algorithm
    est, grid = create_estimator_grid(algorithm_name, algorithm_parameters)
    
    # Create evaluator (Multiclass classification default evaluator, using default metric F1-Score and rest of default parameters: metricLabel=0.0, beta=1.0 and eps=1e-15)
    evaluator = MulticlassClassificationEvaluator()
    
    # Create the cross validator using the estimator, the grid, the evaluator and the selected number of cores and folds 
    cv  = CrossValidatorBestModelTraining(estimator=est, estimatorParamMaps=grid, evaluator=evaluator,
                                          parallelism=algorithm_parameters["parallelism"], numFolds = algorithm_parameters["numFolds"])
    
    # Fit the CV
    cvModel, metrics_cv, bestTrainingModel_train, bestTrainingModel_test, bestIndex2 = cv.fit(preprocessed_dataframe)
    
    #get the best model found in CV
    bestModel = cvModel.bestModel
    
    # Get the predictions and labels of the best training model found in CV
    predictions = bestModel.transform(bestTrainingModel_test)
    
    # get predictions, labels and probabilities as lists
    
    # change it to pandas df
    predictions_pandas = predictions.select("probability", "label", "prediction").toPandas()
    
    ######### Get the most relevant results - multiclass classification #########
    
    # create an empty dictionary that will contain the results of the algorithm execution. . Names of the dictionary variables are set to match with result model's variables name
    multiclass_classification_results_dict = {}

    # average F1 of each validation set of each fold, not training set
    multiclass_classification_results_dict["f1Mean"] = cvModel.avgMetrics[0]
    
    # confusion matrix
    multiclass_classification_results_dict["cmBest"] = plotfunctions.plot_ml("confusionMatrix", 
                                                                             {"data": confusion_matrix(predictions_pandas["label"], predictions_pandas["prediction"]),
                                                                              "xlabel": "Predictions", "ylabel": "Labels"})
    
    # normalized confusion matrix
    multiclass_classification_results_dict["cmNormBest"] = plotfunctions.plot_ml("confusionMatrix", 
                                                                                 {"data": confusion_matrix(predictions_pandas["label"], predictions_pandas["prediction"], normalize='pred'),
                                                                                  "xlabel": "Predictions", "ylabel": "Labels"})
    
    # precision, recall, fscore
    all_metrics = precision_recall_fscore_support(predictions_pandas["label"], predictions_pandas["prediction"])
    
    # Accuracy
    multiclass_classification_results_dict["accuracyBest"] = accuracy_score(predictions_pandas["label"], predictions_pandas["prediction"])
    
    # precision
    multiclass_classification_results_dict["precisionByLabel"] = str(list(all_metrics[0]))
    
    # recall, sensitivity or TP rate
    multiclass_classification_results_dict["recallByLabel"] = str(list(all_metrics[1]))
    
    # FP rate and TN Rate (we get them from cm)
    cmat = confusion_matrix(predictions_pandas["label"], predictions_pandas["prediction"])

    FP = cmat.sum(axis=0) - np.diag(cmat)  
    FN = cmat.sum(axis=1) - np.diag(cmat)
    TP = np.diag(cmat)
    TN = cmat.sum() - (FP + FN + TP)

    # Specificity or true negative rate
    multiclass_classification_results_dict["tnrByLabel"] = str(TN/(TN+FP))
    
    # false positive rate
    multiclass_classification_results_dict["fprByLabel"] = str(FP/(FP+TN))
    
    # F1 measure or F1 Score
    multiclass_classification_results_dict["f1ByLabel"] = str(list(all_metrics[2]))
    
    # get weighted measures
    multiclass_classification_results_dict["precisionWeighted"] = sum(list(all_metrics[0]))/len(list(all_metrics[0]))
    multiclass_classification_results_dict["recallWeighted"] = sum(list(all_metrics[1]))/len(list(all_metrics[1]))
    multiclass_classification_results_dict["tnrWeighted"] = sum(TN/(TN+FP))/len(TN/(TN+FP))
    multiclass_classification_results_dict["fprWeighted"] = sum(FP/(FP+TN))/len(FP/(FP+TN))
    multiclass_classification_results_dict["f1Weighted"] = sum(list(all_metrics[2]))/len(list(all_metrics[2]))
    
    return multiclass_classification_results_dict


"""
######################################### REGRESSION ALGORITHMS #########################################

Function that runs a cross validation based on the regression algorithm received as a parameter. It uses pyspark and returns all the measures founded in the CV.

Parameters:

algorithm_name: string with the algorithm name.
preprocessed_dataframe: preprocessed pyspark dataframe with labels and input data
algorithm_parameters: Dictionary with the algorithm parameters name and values. Name of the dict keys (alg parameters)
can be found in https://spark.apache.org/docs/latest/ml-classification-regression.html 

Return: regression_results_dict: Dictionary with the most important measures. They will be part of the result instance that will be inserted in database:
 - rmseMean - Mean of the RMSE of all models found in CV
 - maeBest - Best Mean Absolute Error value found among all models of CV
 - mapeBest: Best Mean absolute percentage error value found among all models of CV
 - mseBest: Best Mean Squared Error value found among all models of CV
 - rmseBest - Best Root Mean Squared Error, sqrt(MSE) value found among all models of CV
 - r2Best - BestR2 coefficient, coefficient of determination value found among all models of CV
 - regressionPlot - regression plot stirng (png format). Actual values vs predicted values
"""
def regressors(algorithm_name, preprocessed_dataframe, algorithm_parameters):
    
    # create the estimator and grid, depending on the algorithm
    est, grid = create_estimator_grid(algorithm_name, algorithm_parameters)
    
    # Create evaluator (Regression evaluator, using metric RMSE)
    evaluator = RegressionEvaluator()
    
    # Create the cross validator using the estimator, the grid, the evaluator and the selected number of cores and folds 
    cv  = CrossValidatorBestModelTraining(estimator=est, estimatorParamMaps=grid, evaluator=evaluator,
                                                                        parallelism=algorithm_parameters["parallelism"], numFolds = algorithm_parameters["numFolds"])
    
    # Fit the CV
    cvModel, metrics, bestTrainingModel_train, bestTrainingModel_test, bestIndex2 = cv.fit(preprocessed_dataframe)
    
    #get the best model found in CV
    bestModel = cvModel.bestModel
    
    # Get the predictions and labels of the best training model found in CV
    predictions = bestModel.transform(bestTrainingModel_test)
    
    # get predictions, labels and probabilities as lists
    
    # change it to pandas df
    predictions_pandas = predictions.select("label", "prediction").toPandas()
    
    # get predictions and labels
    predictions_list = list(predictions_pandas["prediction"])
    labels_list = list(predictions_pandas["label"])
    
    ######### Get the most relevant results - Regression #########
        
    # create an empty dictionary that will contain the results of the algorithm execution. Names of the dictionary variables are set to match with result model's variables name
    regression_results_dict = {}
    
    # average RMSE of each validation set of each fold, not training set
    regression_results_dict["rmseMean"] = cvModel.avgMetrics[0]

    # MAE - Mean Absolute Error
    regression_results_dict["maeBest"] = mean_absolute_error(labels_list, predictions_list)

    # MAPE - Mean absolute percentage error
    regression_results_dict["mapeBest"] = mean_absolute_percentage_error(labels_list, predictions_list)

    # MSE - Mean Squared Error
    regression_results_dict["mseBest"] = mean_squared_error(labels_list, predictions_list)

    # RMSE - Root Mean Squared Error, sqrt(MSE)
    regression_results_dict["rmseBest"] = math.sqrt(regression_results_dict["mseBest"])

    # R2 coefficient, coefficient of determination
    regression_results_dict["r2Best"] = r2_score(labels_list, predictions_list)
    
    # Plot with predicted and actual values
    labels_list_ordered, predictions_list_ordered = zip(*sorted(zip(labels_list, predictions_list)))
    
    # get the regression plot, actual values vs predicted values
    regression_results_dict["regressionPlot"] = plotfunctions.plot_ml("regressionPlot", {"labels": labels_list_ordered, "predictions": predictions_list_ordered})
    
    return regression_results_dict