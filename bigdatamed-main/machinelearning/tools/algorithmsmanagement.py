# models and forms of the app
from ..forms import *
from ..models import *

# File thar contains the functions for running classification and regression algorithms
from . import sparkmlalgorithms 

# Python useful libraries
import pandas as pd
from io import StringIO
from contextlib import redirect_stdout
import time


"""
Function that creates a dictionary with the available algorithms grouped in 4 categories.

Parameters:

Return:

algorithms_dict: Dictionary with all the available algorithms. It contains 4 keys: logistic_algorithms,
binary_classification_algorithms, multiclass_classification_algorithms and regression_algorithms
"""
def get_available_algorithms():
    
    # Build a dictionary with lists of available algorithms
    algorithms_dict = {}
    algorithms_dict["logistic_algorithms"] = ["BinaryLogisticRegression", "MulticlassLogisticRegression"]
    algorithms_dict["binary_classification_algorithms"] = ["BinaryDecisionTree", "BinaryRandomForest", "BinaryGBT", "BinaryNaiveBayes", "BinaryLinearSVC"]
    algorithms_dict["multiclass_classification_algorithms"] = ["MulticlassDecisionTree", "MulticlassRandomForest", "MulticlassNaiveBayes"]
    algorithms_dict["regression_algorithms"] = ["DecisionTreeRegression", "RandomForestRegression", "GBTRegression"]
    
    return algorithms_dict

"""
Function that selects parameters form for the selected algorithm that receives as a parameter. It can return the char version (it is possible to fill it with post data)
or the non-char version (it is possible to fill it with choices in template)

Parameters:

selected_algorithm: string with the name of the selected algorithm
is_char: boolean that contains if the used requires the char or non char version of the form model.

Return:

form: selected form model.
"""
def select_algorithm_form(selected_algorithm, is_char):
    
    if (selected_algorithm == "BinaryLogisticRegression" or selected_algorithm == "MulticlassLogisticRegression"):
        form = LogisticRegressionForm

    elif (selected_algorithm == "BinaryDecisionTree" or selected_algorithm == "MulticlassDecisionTree"):
        
        if (is_char):
            form = DecisionTreeFormChar
        else:
            form = DecisionTreeForm

    elif (selected_algorithm == "BinaryRandomForest" or selected_algorithm == "MulticlassRandomForest"):                
        
        if (is_char):
            form = RandomForestFormChar
        else:
            form = RandomForestForm

    elif (selected_algorithm == "BinaryGBT"):                
        
        if (is_char):
            form = GBTFormChar
        else:
            form = GBTForm

    elif (selected_algorithm == "BinaryNaiveBayes" or selected_algorithm == "MulticlassNaiveBayes"):                
        
        if (is_char):
            form = NaiveBayesFormChar
        else:
            form = NaiveBayesForm

    elif (selected_algorithm == "BinaryLinearSVC"):
        form = LinearSVCForm

    elif (selected_algorithm == "DecisionTreeRegression"):     
        
        if (is_char):
            form = DecisionTreeFormChar
        else:
            form = DecisionTreeRegressionForm

    elif(selected_algorithm == "RandomForestRegression"):
        form = RandomForestRegressionForm
        
        if (is_char):
            form = RandomForestFormChar
        else:
            form = RandomForestRegressionForm

    elif(selected_algorithm == "GBTRegression"):
        
        if (is_char):
            form = GBTFormChar
        else:
            form = GBTRegressionForm
        
    return form
    

"""
Function that creates a shuffled pandas dataframe from selected variables for running a supervised learning algorithm

Parameters:

variables: selected variables (dictionary with info directly from post with the names of the selected variables of the model)
model: selected model entity
target_variable: string with variable that will act as a target in the algorithm

Return:

df_vars_dict: Dictionary with Shuffled pandas dataframe (df) and two lists with the name of categorical (variables_categoric) and numerical (variables_numeric) variables 
"""
def create_df_pandas(variables, model, target_variable):
    
    # dictionary that contains the return values
    df_vars_dict = {}

    # create a pandas df with the required elements
    df = pd.DataFrame()

    # list of categorical/numerical variables
    variables_numeric = []
    variables_categoric = []

    # iterate and check the selected variables
    for variable in variables:

        # if it is selected
        if (variables[variable] == True):

            selected_text = variable

            # select its type
            variable_type =  model._meta.get_field(variable).get_internal_type()


            # check type of variable and add the column to the dataframe mapping to the correct type
            if (variable_type == "DecimalField"):

                df[variable] = list(map(float, [i[0] for i in list(model.objects.values_list(selected_text))]))
                variables_numeric.append(variable)

            else:

                df[variable] = list(map(str, [i[0] for i in list(model.objects.values_list(selected_text))]))
                variables_categoric.append(variable)

    # Check target variable and select its type
    target_variable_cut = target_variable[0:-6]
    target_variable_type = model._meta.get_field(target_variable_cut).get_internal_type()

    # Add it to the dataframe mapping to the correct type
    if (target_variable_type == "DecimalField"):

        df[target_variable] = list(map(float, [i[0] for i in list(model.objects.values_list(target_variable_cut))]))

    else:

        df[target_variable] = list(map(str, [i[0] for i in list(model.objects.values_list(target_variable_cut))]))

    # shuffle dataset rows
    df = df.sample(frac=1).reset_index(drop=True)
    
    # build the return dictionary
    df_vars_dict["df"] = df
    df_vars_dict["variables_numeric"] = variables_numeric
    df_vars_dict["variables_categoric"] = variables_categoric

    return df_vars_dict

"""
Function that gets information fromm preprocessed pyspark dataframe (algorithm input). It gets the dataframe schema, dimension and first 20 rows
and the internal labelMapping done in classification algorithms.

Parameters:

preprocessed_df: preprocessed pyspark df (created from pandas df obbtaines in function create_df_pandas)
target_variable: name of the variable that will act as a target in the algorithm
is_classification: Indicates whether the problem is a classification one or not.

Return:

preprocessed_df_info_dict: Dictionary with schemas and some other relevant information from the preprocessed pyspark 
df (classification variable mapping, df schema, df 20 first lines, df shape)
"""
def get_df_info(preprocessed_df, target_variable, is_classification):

    preprocessed_df_info_dict = {}
    
    if (is_classification):
                
        # get the variable mapping done by the preprocessing
        tv1 = list(pd.unique(preprocessed_df.select(target_variable).toPandas()[target_variable]))
        tv2 = list(pd.unique(preprocessed_df.select('label').toPandas()['label']))
        preprocessed_df_info_dict["labelMapping"] = dict(zip(tv2,tv1))

    # Get String with schema and 20 first lines and the shape of the pyspark dataframe

    # get schema
    g = StringIO()

    with redirect_stdout(g):
        preprocessed_df.printSchema()

    preprocessed_df_info_dict["dfSchema"] = g.getvalue()

    # get 20 first lines of the dataframe
    f = StringIO()

    with redirect_stdout(f):
        preprocessed_df.show(20)

    preprocessed_df_info_dict["dfShow"] = f.getvalue()

    # get shape
    preprocessed_df_info_dict["dfShape"] = str(preprocessed_df.count()) + " x " + str(len(preprocessed_df.columns))
    
    return preprocessed_df_info_dict

"""
Function that runs the algorithms and stores the results in the database

Parameters:

preprocessed_df: preprocessed pyspark dataframe with correct input for the algorithms
preprocessed_df_info_dict: Dictionary with schemas and some other relevant information from the preprocessed pyspark 
df (classification variable mapping, df schema, df 20 first lines, df shape)
selected_algorithm: name of the selected algorithm for running
post_information: post information with the parameters of the selected algorithm. Filled in template ML_algorithm_set_up.html
model_string: Name of the selected model
algorithms_dict: Dictionary with the available algorithms. 4 fields that appear in function get_available_algorithms.

Return:

result_instance._id: Id of the recent created instance
"""
def run_algorithm(preprocessed_df, preprocessed_df_info_dict, selected_algorithm, post_information, model_string, algorithms_dict):
    
    # begin to count the execution time of the algorithm
    start_time = time.time()

    # dictionary that will contain the parameters for building an instance of the correct algorithm result. Add preprocessed df info
    dict_instance_parameters = {}
    dict_instance_parameters.update(preprocessed_df_info_dict)
        
    # Fill the form with algorithm parameters
    form_model = select_algorithm_form(selected_algorithm, True)
    form = form_model(post_information)
        
    # check whether it's valid:
    if form.is_valid():
        
        # if the form is valid, add the algrithm parameters to the future instance result dictionary
        dict_instance_parameters.update(form.cleaned_data)
        
        #check which is the selected algorithm and which function we have to call
        if (selected_algorithm in algorithms_dict["logistic_algorithms"]):

            if (selected_algorithm == "BinaryLogisticRegression"):
                
                # Run Algorithm
                results_dict = sparkmlalgorithms.binary_log_regression_classifier_cv(preprocessed_df, form.cleaned_data['maxIter'], 
                                                                                                 form.cleaned_data['parallelism'], form.cleaned_data['numFolds'])
                
            elif (selected_algorithm == "MulticlassLogisticRegression"):
                
                # Run Algorithm
                results_dict = sparkmlalgorithms.multiclass_log_regression_classifier_cv(preprocessed_df, form.cleaned_data['maxIter'],
                                                                                                     form.cleaned_data['parallelism'], form.cleaned_data['numFolds'])
                
            # Remove labelMapping parameter from dictionary because the mapping is done automatically by spark's logistic regression algorithm    
            dict_instance_parameters.pop('labelMapping', None)
            
        elif (selected_algorithm in algorithms_dict["binary_classification_algorithms"]):
                        
            # Run Algorithm
            results_dict = sparkmlalgorithms.binary_classifiers(selected_algorithm, preprocessed_df, form.cleaned_data, dict_instance_parameters["labelMapping"])

        elif (selected_algorithm in algorithms_dict["multiclass_classification_algorithms"]):
            
            # Run Algorithm with algorithm name, preprocessed dataframe amd algorithm parameters
            results_dict = sparkmlalgorithms.multiclass_classifiers(selected_algorithm, preprocessed_df, form.cleaned_data)

        elif (selected_algorithm in algorithms_dict["regression_algorithms"]):
        
            # Run Algorithm with algorithm name, preprocessed dataframe amd algorithm parameters
            results_dict  = sparkmlalgorithms.regressors(selected_algorithm, preprocessed_df, form.cleaned_data)
     
    # Add form info and results from the algorithm run 
    dict_instance_parameters.update(results_dict)
    
    # Convert label mapping dictionary into string if it is not a logistic regression or regression algorithm
    if (selected_algorithm == "BinaryLogisticRegression" or selected_algorithm == "MulticlassLogisticRegression"):
        dict_instance_parameters.pop('labelMapping', None)
    elif (not(selected_algorithm in algorithms_dict["regression_algorithms"])):
        dict_instance_parameters["labelMapping"] = str(dict_instance_parameters["labelMapping"])
    
    # Get the modelResult, create an instance and store it in the database
    model_result = globals()[selected_algorithm+"Result"]
    result_instance = model_result.objects.create(model = model_string, executionTime = str(time.time() - start_time), **dict_instance_parameters)

    return result_instance.id