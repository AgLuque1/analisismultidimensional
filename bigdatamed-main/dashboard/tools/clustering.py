# Python Basics
import pandas as pd
import numpy as np

# Plot elbow method figure
import plotnine
from plotnine import *

# Clustring algorithms
from kmodes.kprototypes import KPrototypes

# Clustering results' plots
import seaborn as sns
import matplotlib.pyplot as plt

# Library for managing all types of algorithms (creation of images, preprocessing, etc.)
from . import algorithmsmanagement

# Pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml import Pipeline

from sklearn.preprocessing import MinMaxScaler

# main function that executed the elbow's method
def elbowMethod(filtered_dataframe, meta_description):
    
    # build pandas df
    df = algorithmsmanagement.loadDataframe(filtered_dataframe, False)

    # select categorical/numerical variables
    indices_categorical, indices_numerical = algorithmsmanagement.getCatNumIndices(df.columns, meta_description)

    # get the numpy matrix with normalized values
    scaler, df_matrix = algorithmsmanagement.getNormalizedDfMatrix(df, indices_numerical)

    # get cost of each number of clusters, it will be plot to compute the elbow's method
    cost = []
    for cluster in range(1, 10):
        try:
            kprototype = kprototypesModelTraining({"n_jobs":-1, "n_clusters":cluster, "init":'Huang', "random_state":0},
             df_matrix, indices_categorical)
            cost.append(kprototype.cost_)
        except:
            break

    # get the cost plot, so we can see which is the best value of k (number of clusters)
    image = getCostPlot(cost)

    return image

# function that trains and fit a kprototypes model based on the received parameters
def kprototypesModelTraining(algorithm_parameters, dfMatrix, catColumnsPos):

    # print info about the model that is being trained
    print("Training model with n = ", str(algorithm_parameters["n_clusters"]))
    
    # train and fit the model
    kprototype = KPrototypes(**algorithm_parameters)
    kprototype.fit_predict(dfMatrix, categorical = catColumnsPos)
    
    return kprototype

# Funtion that gets the image associated to the cost plot, where the user can see the "elbow"
def getCostPlot(cost):

    # get the cost plot, so we can see which is the best value of k (number of clusters)
    df_cost = pd.DataFrame({'Cluster':range(1, 10), 'Cost':cost})
    plotnine.options.figure_size = (8, 4.8)
    figure_cost = (
        ggplot(data = df_cost)+
        geom_line(aes(x = 'Cluster',
                      y = 'Cost'))+
        geom_point(aes(x = 'Cluster',
                       y = 'Cost'))+
        geom_label(aes(x = 'Cluster',
                       y = 'Cost',
                       label = 'Cluster'),
                   size = 10,
                   nudge_y = 1000) +
        labs(title = 'Optimal number of cluster with Elbow Method')+
        xlab('Number of Clusters k')+
        ylab('Cost')+
        theme_minimal()
    )

    # get the image in png format
    image = algorithmsmanagement.getImage(figure_cost.draw())

    return image

# Function that runs the algorithm Kprototypes and gets the most relevant results stored in a dictionary
def getKprototypesClusteringResults(algorithm_parameters, dfMatrix, catColumnsPos, numColumns, initial_dataset, scaler):

    # build the kprototype model and train it
    kprototype = kprototypesModelTraining(algorithm_parameters, dfMatrix, catColumnsPos)
    
    # create an empty result variable that will contain all the information for the return
    result = {}

    # copy the initial dataset because it is going to be modified
    df = initial_dataset.copy()

    # add the model to the results dict
    result["kprototype"] = kprototype
    
    # get denormalized centroids
    denormalized_centroids = kprototype.cluster_centroids_.copy()
    denormalized_centroids = scaler.inverse_transform(kprototype.cluster_centroids_[0:,0:len(numColumns)])
    denormalized_centroids = np.concatenate((denormalized_centroids, kprototype.cluster_centroids_[0:, len(numColumns):]),axis=1)

    # add denormalized centroids to the dict
    result["denormalized_centroids"] = denormalized_centroids

    # get the map of the labels depending on the selected number of clusters
    map_labels = {}
    for i in range(kprototype.get_params()["n_clusters"]):
        map_labels[i] = "Cluster" + str(i+1)

    # Add the cluster labels to the dataframe (Numeric) and map them with the map obtained previously (String)
    df['Cluster Labels Numeric'] = kprototype.labels_
    df['Cluster Labels'] = df['Cluster Labels Numeric'].map(map_labels)    

    # Order the cluster's labels

    df['Cluster Labels'] = df['Cluster Labels'].astype('category')
    df['Cluster Labels'] = df['Cluster Labels'].cat.reorder_categories(list(map_labels.values()))

    # Add the cluster labels to the initial df
    result["dataset_w_cluster_labels"] = df.copy()

    # Cluster interpretation, cluster summary in a table df.columns[indices_numerical]
    df.rename(columns = {'Cluster Labels Numeric':'Total'}, inplace = True)

    # get the dictionary for the groupby/aggregation operation (summary/interpretation of obteined clusters)
    dict_agg = {'Total':'count'}
    for varNum in numColumns:
        dict_agg[varNum] = 'mean'
    for varCat in df.columns[catColumnsPos]:
        dict_agg[varCat] = lambda x: x.value_counts().index[0]

    cluster_interpretation = df.groupby('Cluster Labels').agg(dict_agg).reset_index()

    # normalized cluster interpretation
    result["normalized_cluster_interpretation"] = cluster_interpretation.copy()

    # get denormalized cluster interpretation: cluster centroids and mean values of each cluster
    cluster_interpretation[numColumns] = scaler.inverse_transform(cluster_interpretation[numColumns])

    # denormalized cluster interpretation
    result["denormalized_cluster_interpretation"] = cluster_interpretation.copy()
    
    # denormalized data (optional)
    result["dataset_w_cluster_labels"][numColumns] = scaler.inverse_transform(result["dataset_w_cluster_labels"][numColumns])
    
    return result

# Function that transform the clustering results into results that will be included in the app (HTML code)
def getAppResults(result, cat_cols, num_cols):

    # initialize the return dictionary
    results_app = {}

    # Cluster centorids
    results_app["cluster_centroids"] = result["kprototype"].cluster_centroids_.tolist()
    # denormalized cluster centroids
    results_app["denormalized_centroids"] = result["denormalized_centroids"].tolist()
    # header of the cluster centroids table
    results_app["centroids_table_header"] = num_cols.tolist() + cat_cols.tolist()
    # Check the iteration of the clusters created
    results_app["n_iter"] = result["kprototype"].n_iter_
    # Check the cost of the clusters created
    results_app["cost"] = result["kprototype"].cost_
    # df head con las labels ya adheridas al dataset inicial
    results_app["dataset_w_cluster_labels"] = result["dataset_w_cluster_labels"].head().to_html()
    # print normalized results
    results_app["normalized_cluster_interpretation"] = result["normalized_cluster_interpretation"].to_html()
    # print denormalized results
    results_app["denormalized_cluster_interpretation"] = result["denormalized_cluster_interpretation"].to_html()

    return results_app

# function for getting the image with a summary of clustering's numerical variables
def getPairPlot(result, n_clusters, numCols, color_palette):

    if (len(numCols) > 1):

        # set up figure/image size - 2000x2000 aprox
        plt.rcParams['figure.figsize'] = [20, 20]
        plt.rcParams['figure.dpi'] = 100

        # set up the font dimensions
        sns.set(font_scale = 1.9-0.1*len(numCols))

        # set up the pairplot
        g1 = sns.pairplot(result["dataset_w_cluster_labels"].drop(columns=['Cluster Labels Numeric']),
                        hue="Cluster Labels", palette=color_palette[0:n_clusters], 
                        plot_kws={'alpha': 0.7, 'edgecolor': 'grey', "linewidth":0.5}, diag_kws={'alpha':0.1, "linewidth":1.5},
                        height=20/len(numCols), aspect=20/22)                   
        g1.fig.suptitle("Resumen de variables numéricas - Resultados con " + str(n_clusters)+ " clusters", y=1.02, size=25)

        # get the figure
        fig = plt.gcf()

        # get the image
        num_image = algorithmsmanagement.getImage(fig)

    elif (len(numCols) == 1):

        # set up figure/image size - 1000x1000 aprox
        plt.rcParams['figure.figsize'] = [10, 10]
        plt.rcParams['figure.dpi'] = 100

        # set up the font scaling
        sns.set(font_scale = 1.5)

        # get density plot
        g1 = sns.displot(result["dataset_w_cluster_labels"].drop(columns=['Cluster Labels Numeric']), 
        x=numCols[0], hue="Cluster Labels", kind="kde", fill=True, color = color_palette[0:n_clusters], alpha=0.1,
        height = 10, aspect=(10/11.5))
        g1 = g1.fig.suptitle("Resumen de variables numéricas - Resultados con " + str(n_clusters)+ " clusters", y=1.04, size=15)

        # get the figure
        fig = plt.gcf()

        # get the image
        num_image = algorithmsmanagement.getImage(fig)

    else:

        num_image = None
    
    return num_image

# function for getting the image with a summary of clustering's categorical variables
def getStackedBarPlot(result, catCols, dict_params, color_palette):

    # if there is more than 2 categorical variables, generate a stacked bar plot
    if (len(catCols) > 1):

        # get all the possible combinations of categorical variables
        combinations = []
        for i in range(len(catCols)):
            for j in range(i):
                if (catCols[i] != catCols[j]):
                    combinations.append([catCols[j], catCols[i]])
        combinations = sorted(combinations)

        # set up the position of each combination (each combination in cols and one row for each cluster)
        positions = []
        for j in range(dict_params["n_clusters"]):
            list_aux = []
            for k in range(len(combinations)):
                list_aux.append([j,k])
            positions.append(list_aux)

        # set up the image dimension
        plt.rcParams['figure.figsize'] = [15, 10]
        plt.rcParams['figure.dpi'] = 100

        # set up the subplots, nclust x ncombinations
        fig, axs = plt.subplots(dict_params["n_clusters"], len(combinations))

        # set up the title of the whole plot
        _ = fig.suptitle("Resumen de variables categóricas - Resultados con " + str(dict_params["n_clusters"]) + " clusters", y=1.04, size=20)

        for label in range(dict_params["n_clusters"]):
            
            for comb_pos in zip(combinations, positions[label]):
                    
                # Creating crosstab
                crosstb = pd.crosstab(result["dataset_w_cluster_labels"]
                                    [ result["dataset_w_cluster_labels"]["Cluster Labels Numeric"] == label][comb_pos[0][0]],
                                    result["dataset_w_cluster_labels"]
                                    [ result["dataset_w_cluster_labels"]["Cluster Labels Numeric"] == label][comb_pos[0][1]])

                # Creating barplot
                _ = crosstb.plot(kind="bar", stacked=True, rot=0, ax=axs[comb_pos[1][0],comb_pos[1][1]], color = color_palette[0:dict_params["n_clusters"]], edgecolor = "grey" )

        # get the figure
        fig = plt.gcf()
        
        # get the image
        cat_image = algorithmsmanagement.getImage(fig)

    # if there is one categorical variable, generate a bar plot
    elif (len(catCols) == 1):
        
        # set up image dimension
        plt.rcParams['figure.figsize'] = [15, 15]
        plt.rcParams['figure.dpi'] = 100

        # build a new figure
        plt.figure()

        # create the barplot and set its title
        plt.bar(result["dataset_w_cluster_labels"][catCols[0]].value_counts().index, result["dataset_w_cluster_labels"][catCols[0]].value_counts(),
         align='center', alpha=0.5, color = color_palette[0])
        plt.suptitle("Resumen de variables categóricas - Resultados con " + str(dict_params["n_clusters"]) + " clusters", size=25, y=0.92);      

        # set up image dimension
        fig = plt.gcf()
        
        # get the image
        cat_image = algorithmsmanagement.getImage(fig)

    else:

        cat_image = None


    return cat_image

# function for getting the image with a summary of clustering's numerical/categorical variables
def getBoxPlot(result, dict_params, catCols, numCols, color_palette):

    if (len(catCols) > 0 and len(numCols) > 0):

        # set up seaborn and its images dimension
        plt.rcParams['figure.figsize'] = [20, 20]
        plt.rcParams['figure.dpi'] = 100
        sns.set_theme(style="whitegrid")

        if (len(catCols) == 1 and len(numCols) != 1):
            aspect_ratio = 30/21
        else:
            aspect_ratio = 20/21

        # set up the PairGrid that will contain the boxplot
        g = sns.PairGrid(data=result["dataset_w_cluster_labels"], x_vars=catCols,
                        y_vars=numCols, hue="Cluster Labels", height=20/len(numCols), aspect=aspect_ratio,
                        palette = color_palette)

        # set up the upper title of the figure
        _ = g.fig.suptitle("Resumen de variables numéricas/categóricas - Resultados con " + str(dict_params["n_clusters"]) + " clusters", y=1.01, size=16)

        # add legend manually, using the color of the color_palette
        g = g.add_legend(fontsize=14) 
        for i in range(dict_params["n_clusters"]):
            g._legend.legendHandles[i].set_facecolor(color_palette[i])
            g._legend.legendHandles[i].set_edgecolor("#000000")
            g._legend.legendHandles[i].set_alpha(1)
            g._legend.legendHandles[i].set_linewidth(1)
        
        # map the pairgrid into boxplot
        figure_cat_num = g.map(sns.boxplot, boxprops = dict(linewidth=1, edgecolor='black'), flierprops = dict(markeredgewidth=1, markerfacecolor='grey', markeredgecolor='black'),
            medianprops = dict(color='black', linewidth=1), whiskerprops = dict(color='black', linewidth=1), capprops = dict(color='black', linewidth=1))

        # get the seaborn figure and the image
        fig = figure_cat_num.figure
        cat_num_image = algorithmsmanagement.getImage(fig)

    else:

        cat_num_image = None

    return cat_num_image

# Function that handles all the operations related with the run of the local KPrototypes algorithm and getting the results
def runKPrototypes(filtered_df, meta_description, algorithm_parameters, null_parameters):

    # initialize result dictionary
    result_dict = {}

    # build pandas df
    df = algorithmsmanagement.loadDataframe(filtered_df, True)
    
    # drop numerical null values (categorical not included from API filter function)
    df = df.dropna()

    # select categorical/numerical variables
    indices_categorical, indices_numerical = algorithmsmanagement.getCatNumIndices(df.columns, meta_description)

    # check if the user makes the parameters to run the algorithm
    if (len(indices_categorical) == 0):
        return {'success': True, 'info_user':'Si únicamente ha seleccionado variables numéricas, considere utilizar el algoritmo KMeans'}
    elif (len(indices_numerical) == 0):
        return {'success': True, 'info_user':'Si únicamente ha seleccionado variables categóricas, considere utilizar el algoritmo KMeans'}
    
    # get the numpy matrix with normalized values
    scaler, df_matrix = algorithmsmanagement.getNormalizedDfMatrix(df, indices_numerical)
    
    # get the parameters (also null ones) for the algorithm
    dict_params = eval(algorithm_parameters)

    for key in eval(null_parameters).keys():
        dict_params[key] = None

    # run the algorithm and store the results
    result = getKprototypesClusteringResults(dict_params, df_matrix, indices_categorical, df.columns[indices_numerical], df, scaler)
    
    # prepare the previous results so they can be sent to the app
    results_app = getAppResults(result, df.columns[indices_categorical], df.columns[indices_numerical])

    # get the 3 images: pairplot (numeric-numeric), stacked bar plot (cat-cat) and boxplot (numeric-cat)
    
    # set up the color palette for the images (up to 5 clusters right now)
    color_palette = ["#ABDEE6", "#FFC8A2", "#CCE2CB", "#FF968A", "#CBAACB"]

    # image 1 - pairplot (numeric-numeric) clustering summary
    num_image = getPairPlot(result, dict_params["n_clusters"], df.columns[indices_numerical], color_palette)

    # image 2 - stacked bar plot (cat-cat) clustering summary
    cat_image = getStackedBarPlot(result, df.columns[indices_categorical], dict_params, color_palette)

    # image 3 - boxplot (numeric-cat) clustering summary
    cat_num_image = getBoxPlot(result, dict_params, df.columns[indices_categorical], df.columns[indices_numerical], color_palette)

    return {'success': True, 'num_image': num_image, 'cat_image':cat_image, 'cat_num_image':cat_num_image, "results_app":results_app}

# Function that handles all the operations related with the run of the distributed Kmeans algorithm and getting the results
def runKmeansDistributed(filtered_df, meta_description, algorithm_parameters, null_parameters):

    # get the parameters (also null ones) for the algorithm
    dict_params = eval(algorithm_parameters)

    for key in eval(null_parameters).keys():
        dict_params[key] = None

    # add the features parameter
    dict_params["featuresCol"] = "features"

    # create spark session

    # distributed spark session, with the configuration from the ClusterSetUp view
    if (dict_params["distributedExecution"]):

        # vuild the configuration variable with the values introduced by the user in the client
        conf = SparkConf().setMaster(dict_params["masterURL"]).setAppName(dict_params["appName"])

        if (dict_params["maxCores"] != None):
            conf.set("spark.cores.max", str(dict_params["maxCores"]))

        conf.set("spark.executor.cores", str(dict_params["executorCores"]))
        conf.set("spark.executor.memory", str(dict_params["executorMemory"])+dict_params["executorMemoryUnit"])

        # create the spark session with the configuration variable
        spark = SparkSession.builder.config(conf = conf).appName(dict_params["appName"]).getOrCreate()

        # remove all the parameters related with the distributed execution from the parameter dictionary, so the algorithm only uses the
        # correct ones 
        for param in algorithmsmanagement.getDistributedParameters().keys():
            dict_params.pop(param, None)

    # local spark session (using all the cores and a single executor)
    else:

        spark = SparkSession.builder.getOrCreate()

    # remove the checkbox information from the parameter dictionary
    dict_params.pop("distributedExecution", None)
    
    # check details of configuration and get spark context
    sc = spark.sparkContext

    # build pandas df
    df = algorithmsmanagement.loadDataframe(filtered_df, True)

    # drop numerical null values (categorical not included from API filter function)
    df = df.dropna()

    # keep the original variables
    original_variables = df.columns

    # check that only numerical variables are used
    indices_categorical, indices_numerical = algorithmsmanagement.getCatNumIndices(df.columns, meta_description)
    
    if (len(indices_categorical) > 0):
        return {'success': True, 'info_user':'Kmeans no permite el uso de variables categóricas. Considere usar Kprototypes o Kmodes.'}

    # normalize the columns of the dataframe with MinMax scaler
    scaler = MinMaxScaler()
    df[df.columns] = scaler.fit_transform(df[df.columns])

    # get pyspark df
    df_spark = spark.createDataFrame(df) 

    # spark preprocessing: get features col (all df columns in a single one named features)
    assembler = VectorAssembler(inputCols=df.columns.to_list(), outputCol="features")
    stages = [assembler]

    # Pipeline: It consists in a sequence of PipelineStages (Transformers and Estimators) to be run in a specific order. 
    # Build the pipeline and apply it

    pipeline = Pipeline(stages = stages)
    pipelineModel = pipeline.fit(df_spark)
    df_spark_preprocessed = pipelineModel.transform(df_spark)

    # run the algorithm and store the results
    result = getKmeansDistributedClusteringResults(dict_params, original_variables, df, df_spark_preprocessed, scaler, algorithm_parameters)

    # stop the spark context
    sc.stop()

    # prepare the previous results so they can be sent to the app
    results_app = getAppResultsKmeans(result, original_variables)

    # set up the color palette for the images (up to 5 clusters right now)
    color_palette = ["#ABDEE6", "#FFC8A2", "#CCE2CB", "#FF968A", "#CBAACB"]

    # get the pairplot pairplot (numeric-numeric) clustering summary
    num_image = getPairPlot(result, dict_params["k"], original_variables, color_palette)

    return {'success': True, 'num_image': num_image, "results_app":results_app}


# Function that gets the results of the Kmeans Distributed algorithm
def getKmeansDistributedClusteringResults(dict_params, original_variables, df, df_spark_preprocessed, scaler, algorithm_parameters):

    # Trains a k-means model.
    kmeans = KMeans(**dict_params)
    model = kmeans.fit(df_spark_preprocessed)

    # Make predictions
    predictions = model.transform(df_spark_preprocessed)

    # get results of the algorithm
    result = {}

    # get the silhouette measure using the clustering evaluator
    if (dict_params['distanceMeasure'] == "euclidean"):
        distance_evaluator = "squaredEuclidean"
    else:
        distance_evaluator = "cosine"

    evaluator = ClusteringEvaluator(distanceMeasure=distance_evaluator)
    result["silhouette"] = evaluator.evaluate(predictions)

    # get centroids
    centers = model.clusterCenters()
    centers_aux = []
    for center in centers:
        centers_aux.append(center)
    centroids = np.array(centers_aux)

    # get the map of the labels depending on the selected number of clusters
    map_labels = {}
    for i in range(eval(algorithm_parameters)["k"]):
        map_labels[i] = "Cluster" + str(i+1)

    # Add the cluster labels to the dataframe (Numeric) and map them with the map obtained previously (String)
    df['Cluster Labels Numeric'] = np.array(predictions.select("prediction").toPandas())
    df['Cluster Labels'] = df['Cluster Labels Numeric'].map(map_labels)    

    # Order the cluster's labels
    df['Cluster Labels'] = df['Cluster Labels'].astype('category')
    df['Cluster Labels'] = df['Cluster Labels'].cat.reorder_categories(list(map_labels.values()))
    
    # Add the cluster labels to the initial df
    result["dataset_w_cluster_labels"] = df.copy()

    # add the (normalized) centroids
    result["centroids"] = centroids

    # get denormalized centroids
    result["denormalized_centroids"] = scaler.inverse_transform(centroids)

    # Cluster interpretation, cluster summary in a table df.columns[indices_numerical]
    df.rename(columns = {'Cluster Labels Numeric':'Total'}, inplace = True)

    # get the dictionary for the groupby/aggregation operation (summary/interpretation of obteined clusters)
    dict_agg = {'Total':'count'}
    dict_agg.update(dict(zip(original_variables, ["mean"]*len(original_variables))))

    cluster_interpretation = df.groupby('Cluster Labels').agg(dict_agg).reset_index()
    
    # normalized cluster interpretation
    result["normalized_cluster_interpretation"] = cluster_interpretation.copy()

    # get denormalized cluster interpretation: cluster centroids and mean values of each cluster
    cluster_interpretation[original_variables] = scaler.inverse_transform(cluster_interpretation[original_variables])

    # denormalized cluster interpretation
    result["denormalized_cluster_interpretation"] = cluster_interpretation.copy()
    
    # denormalized data (optional)
    result["dataset_w_cluster_labels"][original_variables] = scaler.inverse_transform(result["dataset_w_cluster_labels"][original_variables])

    return result

# function that gets the results of the kmeans algorithm ready to send it to the client
def getAppResultsKmeans(result, original_variables):

    # initialize the return dictionary
    results_app = {}

    # Cluster centorids
    results_app["cluster_centroids"] = result["centroids"].tolist()
    # denormalized cluster centroids
    results_app["denormalized_centroids"] = result["denormalized_centroids"].tolist()
    # header of the cluster centroids table
    results_app["centroids_table_header"] = original_variables.tolist()
    # Check the cost of the clusters created
    results_app["silhouette"] = result["silhouette"]
    # df head con las labels ya adheridas al dataset inicial
    results_app["dataset_w_cluster_labels"] = result["dataset_w_cluster_labels"].head().to_html()
    # print normalized results
    results_app["normalized_cluster_interpretation"] = result["normalized_cluster_interpretation"].to_html()
    # print denormalized results
    results_app["denormalized_cluster_interpretation"] = result["denormalized_cluster_interpretation"].to_html()

    return results_app
