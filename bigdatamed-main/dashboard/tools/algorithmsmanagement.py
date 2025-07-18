import pandas as pd
import io
import urllib, base64
from sklearn.preprocessing import MinMaxScaler

# function that gets the available algorithms of the problem string that receives as a parameter
def getAvailableAlgorithms(problem_string):

    if (problem_string == "Clasificacion"):
        available_algorithms = ["Binary Logistic Regression", "Multiclass Logistic Regression", "Binary Decision Tree",
         "Multiclass Decision Tree", "Binary Random Forest", "Multiclass Random Forest", "Binary Gradient Boosting Tree",
          "Binary Naive Bayes", "Multiclass Naive Bayes", "Binary Linear Support Vector Classification"]
    elif (problem_string == "Regresion"):
        available_algorithms = ["Decision Tree", "Random Forest", "Gradient Boosting Tree"]
    elif (problem_string == "Clustering"):
        available_algorithms = ["Kmeans", "Kmodes", "Kprototypes", "KmeansDistributed"]        
    elif (problem_string == "EDA"):
        available_algorithms = []

    return available_algorithms

# function that gets the parameters of the algorithms associated to the selected problem
# Integer: parameter type, default value, min value (optional), max value (optional)
# Float: parameter type, default value, min value (optional), max value (opyional)
# Choice: parameter type, array of choices (first one will be the default option)
# Boolean: parameter type, default value (True or False)
# String: parameter type, default value
def getAlgorithmParameters(problem_string):

    if (problem_string == "Clasificacion"):
        algorithm_parameters = {}
    elif (problem_string == "Regresion"):
        algorithm_parameters = {}
    elif (problem_string == "Clustering"):
        algorithm_parameters = {
            "Kmeans": {
                "n_clusters":{"data":["Integer", 8, 1], "doc":"n_clusters doc esto es una prueba"}, 
                "init": {"data":["Choice", ['kmeans++', 'random']], "doc":"init doc"},
                'n_init': {"data":["Integer", 10, 1], "doc":"n_init doc"},
                'max_iter': {"data":["Integer", 300, 1], "doc":"max_iter doc"},
                'tol': {"data":["Float", 0.0004, 0], "doc":"tol doc"},
                'random_state': {"data":["Integer", 0, 0], "doc":"random_state doc"},
                'copy_x': {"data":["Boolean", True], "doc":"copy_x doc"},
                'algorithm': {"data":["Choice", ["auto", "full", "elkan"]], "doc":""}
            },
            "Kmodes": {
                "n_clusters": {"data":["Integer", 8, 1], "doc":""}, 
                "max_iter": {"data":["Integer", 100, 1], "doc":""}, 
                "init": {"data":["Choice", ["Cao", "Huang", "random"]], "doc":""},
                "n_init": {"data":["Integer", 10, 1], "doc":""}, 
                'random_state': {"data":["Integer", 0, 0], "doc":""},
                "n_jobs": {"data":["Integer", 1, -1], "doc":""}, 
            },
            "Kprototypes":{
                "n_clusters": {"data":["Integer", 8, 1], "doc":""}, 
                "max_iter": {"data":["Integer", 100, 1], "doc":""}, 
                "init": {"data":["Choice", ["Cao", "Huang", "random"]], "doc":""},
                "gamma": {"data":["Float", None, 0], "doc":""},
                "n_init": {"data":["Integer", 10, 1], "doc":""}, 
                'random_state': {"data":["Integer", 0, 0], "doc":""},
                "n_jobs": {"data":["Integer", 1, -1], "doc":""},
            },
            "KmeansDistributed":{
                "k": {"data":["Integer", 2, 1], "doc":""},
                "initMode": {"data":["Choice", ["k-means||", "random"]], "doc":""},
                "seed": {"data":["Integer", None], "doc":""}, 
                "initSteps":  {"data":["Integer", 2, 1], "doc":""}, 
                "tol": {"data":["Float", 0.0001, 0], "doc":""},
                "distanceMeasure": {"data":["Choice", ["euclidean", "cosine"]], "doc":""},
                "maxIter": {"data":["Integer",  20, 0], "doc":""},
                "distributedExecution": {"data":["Boolean", False], "doc":""}
            }
        }
    elif (problem_string == "EDA"):
        algorithm_parameters = {}

    return algorithm_parameters

# function that gets the parameters for configuring a distributed algorithm's run
# Integer: parameter type, default value, min value (optional), max value (optional)
# Float: parameter type, default value, min value (optional), max value (opional)
# Choice: parameter type, array of choices (first one will be the default option)
# Boolean: parameter type, default value (True or False)
# String: parameter type, default value
def getDistributedParameters():

    return {
                "masterURL": {"data":["String", "spark://"], "doc":""},
                "maxCores": {"data":["Integer", None, 1], "doc":""},
                "executorCores": {"data":["Integer", 2, 1], "doc":""}, 
                "executorMemory":  {"data":["Integer", 2, 1], "doc":""}, 
                "executorMemoryUnit": {"data":["Choice", ["g", "t", "m", "k"]], "doc":""},
                "appName": {"data":["String", "App from AIMDP"], "doc":""},
            }

# Function that loads and stores in memory the dataframe and preprocess it if needed
def loadDataframe(filtered_dataframe, preprocessing):
    import ipdb; ipdb.set_trace();
    df = pd.DataFrame(filtered_dataframe)
    df = df.drop(columns=["_id"])

    df = df.dropna()

    if (preprocessing):

        # preprocessing - PAISNAC label
        if("PAISNAC" in list(df.columns)):
            countries = df["PAISNAC"].unique()
            dict_countries = {}
            for elem in countries:
                dict_countries[elem] = elem
                
            if ("United Kingdom of Great Britain and Northern Ireland (the)" in countries):
                dict_countries["United Kingdom of Great Britain and Northern Ireland (the)"] = "UK"
                df['PAISNAC'] = df['PAISNAC'].map(dict_countries)

        # preprocessing - SEXO1N label
        if("SEXO1N" in list(df.columns)):
            df['SEXO1N'] = df['SEXO1N'].map({1.0:'Hombre', 2.0:'Mujer', 3.0:'Indeterminado'})

    return df

# Function that transforms a pandas df to a numpy matrix with the numerical variables normalized
def getNormalizedDfMatrix(df, indices_numerical):

    # normalize numerical columns with MinMax scaler
    scaler = MinMaxScaler()
    import ipdb; ipdb.set_trace();
    df[df.columns[indices_numerical]] = scaler.fit_transform(df[df.columns[indices_numerical]])

    # transform it into a Matrix
    df_matrix = df.to_numpy()

    return scaler, df_matrix
 

# Function that provides information about which variables of the selected ones are numerical or categorical, based on the meta info
def getCatNumIndices(df_columns, meta_description):

    indices_categorical = []
    indices_numerical = []
    for i in range(len(df_columns)):
        for meta_instance in meta_description:
            if (meta_instance['Code']==df_columns[i]):

                if (meta_instance["VarType"] == "Categorical"):
                    indices_categorical.append(i)
                elif (meta_instance["VarType"] == "Numerical"):
                    indices_numerical.append(i)

                break

    return indices_categorical, indices_numerical

# Function that gets the PNG image of the one that gets as a parameter
def getImage(fig):

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    image = urllib.parse.quote(string)

    return image
