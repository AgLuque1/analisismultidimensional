from urllib import request
from flask import jsonify
from flask import Blueprint
from flask_restx import Api, Resource
from flask import request
# from app import api
from app.lib.database import database as dbases
from app.lib.machinelearning.unsupervised import clustering as clustering

from bson import json_util
import pandas as pd

import json

import numpy as np

bigdatamed_bp = Blueprint('bigdatamed', __name__)

api = Api( bigdatamed_bp )
ns_bigdatamed = api.namespace('bigdatamed', "Proyect api dashboard BIGDATAMED: Data Analytics in Medicine: from medical records to Big Data")


@ns_bigdatamed.route('/getDBs',endpoint="getDBsBigDataMed")
@ns_bigdatamed.doc(description="Nombre de las bases de datos")
class getNameDataBase(Resource):
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer las bases de datos correspondientes
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
    
    def get(self):
        DB = dbases.database()
        dbs = DB.list_name_database()
        list_dbName = []
        # To DO:
        for db in dbs:
            database ={db:db}
            list_dbName.append(database)
        return jsonify(list_dbName)


@ns_bigdatamed.doc(description="Nombre de las bases de datos")
@ns_bigdatamed.route('/<name>/data/')
class getData(Resource):
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer los datos correspondientes de la base de datos seleccionada
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
    def __init__(self,name):
        self.name = name
 
    def get(self,name):
        DB = dbases.database()
        data = DB.get_data(name)

        collection = json.loads(json_util.dumps(data))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Nombre de las columnas de la base de datos")
@ns_bigdatamed.route('/<name>/meta/')
class getMeta(Resource):
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer los datos correspondientes de la base de datos seleccionada
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
 
    def get(self,name):
        DB = dbases.database()
        data = DB.get_meta(name)
        data_db = []
        # To DO:
        for db in data:
            data_db.append(db)

        collection = json.loads(json_util.dumps(data_db))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Conteo de los valores de una variable categórica")
@ns_bigdatamed.route('/<name>/<variable>/countCategories')
class getCount(Resource):
 
    def get(self, name, variable):
        DB = dbases.database()
        data = DB.get_count(name, variable)

        collection = json.loads(json_util.dumps(data))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Obtención de los valores necesarios para la construcción de un histograma. Número de intervalos basado en Juran's Quality Control Handbook.")
@ns_bigdatamed.route('/<name>/<variable>/histogram')
class getHistogram(Resource):
 
    def get(self, name, variable):

        DB = dbases.database()

        # calculate the size of the sample, the number of non null values of the variable that is going to be represented in the histogram
        n_cursor = DB.get_number_documents_var_not_null(name, variable)
        n = json.loads(json_util.dumps(n_cursor))[0]["numbernotnull"]
        
        # Calculate number of bins of the histogram, based on https://www.qimacros.com/control-chart-formulas/histogram-bars/
        if (n > 1000):
            nbins = 11
        elif( n > 500):
            nbins = 10
        elif (n > 200):
            nbins = 9
        elif (n > 100):
            nbins = 8
        elif (n > 50):
            nbins = 7
        else:
            nbins = 6

        # get the maximum and minimum values of the variable that is going to be plotted
        max_min_cursor = DB.get_max_min(name, variable)
        max_min_dict = json.loads(json_util.dumps(max_min_cursor))[0]

        # Build the intervals with integers, divide the domain (from minimum value to max value + 1) in nbins equal parts
        arr_bins = np.array_split(range(int(max_min_dict["min"]), int(max_min_dict["max"])+2), nbins)

        # convert the intervals with the values of the domain from a list of numpy array into a list of lists structure
        list_aux = [l.tolist() for l in arr_bins]

        # Remove empty lists in case that there are more bins than different values in the variable
        list_aux_clean = [x for x in list_aux if x]

        # If the length of the first interval is 1, all the intervals are going to have the same length, so we create the 
        # final bin list (mongodb bucket boundary style) introducing all the numbers of the domain in a list
        if (len(list_aux_clean[0]) == 1):
            list_bins = []
            for sublist in list_aux_clean:
                list_bins.extend(sublist)

        # If the length is not 1, some intervals are going to have length > 1, so we create the final bin list
        # by adding the first number of each interval to a new list (mongodb bucket boundary style)
        else:
            list_bins = [l[0] for l in arr_bins]

            # If the length of the last interval is more than one, create an extra one so the last interval is closed: [i1, i2), ..., [in-1, in]
            if (len(list_aux_clean[-1]) > 1):
                list_bins = list_bins + [int(max_min_dict["max"]+1)]

        # Get the type of variable and map the values to the list to the correct type
        variable_type = json.loads(json_util.dumps(DB.get_type_not_null(name, variable)))[0]['fieldType']
        if (variable_type == 'double'):
            list_bins = list(map(float, list_bins))
        else:
            list_bins = list(map(int, list_bins))

        # Get the number of instances that belongs to each interval
        data = DB.get_histogram(name, variable, list_bins)

        collection = json.loads(json_util.dumps(data))

        histogram_data_list = []
        # Add the intervals without numbers to the histogram data list
        for bin in list_bins:

            found = False
            i = 0
            while ( (not found) and (i < len(collection)) ):
                if (collection[i]['_id'] == bin):
                    found = True
                    histogram_data_list.append(collection[i]['count'])
                i+=1

            if (not found):
                # collection.append({'_id':bin, 'count':0})
                histogram_data_list.append(0)

        response_dict = {}
        response_dict['histogram_data'] = histogram_data_list
        response_dict['histogram_bins'] = list_bins

        return jsonify(response_dict)

@ns_bigdatamed.doc(description="Obtención de los nombres detallados de las bases de datos del sistema a las que tiene acceso el usuario.")
@ns_bigdatamed.route('/getUserDBVerbose')
class getUserDBVerbose(Resource):
 
    def get(self):
        DB = dbases.database()
        data = DB.get_UserDBVerbose()

        collection = json.loads(json_util.dumps(data))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Obtención de los nombres detallados de las bases de datos del sistema a las que tiene acceso el administrador.")
@ns_bigdatamed.route('/getAdminDBVerbose')
class getAdminDBVerbose(Resource):
 
    def get(self):
        DB = dbases.database()
        data = DB.get_AdminDBVerbose()
        
        collection = json.loads(json_util.dumps(data))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Obtener de la variable seleccionada, sus metadatos y sus valores sin repetir")
@ns_bigdatamed.route('/<db>/<name_variable>/')
class getValuesCategory(Resource):
    """ Service that prepares the data to filter by rows within our dataset.

    Args:
        Resource (_Service_):  Service that prepares the data to filter by rows within our dataset.
    """
    def get(self,db,name_variable):
        """ Service that prepares the data to filter by rows within our dataset.
            Struct description_values: Dictionary store default data, show as first element in front-end.
            
        Args:
            db (string): Name DataBase
            name_variable (string): Name Column DataSet

        Returns: _type_: _description_ariable it can be:
             - Categorical:   Display the different values without repeating.
             - Numerical:     Display the maximum and minimum of the values in that column.
             - Identificador: Show empty, because all data in the rows are different.
        """
        DB = dbases.database()
        
        meta_values = DB.get_meta_variable(db,name_variable)
        data_values = DB.get_values_variable(db,name_variable)

        # Dictionary store metaData and distinct values of dataset
        descripcion_values = {}
        descripcion_values['values'] = []

        
        # Meta values variables dataset
        for meta in meta_values:
            descripcion_values['VarType'] = meta['VarType']
            descripcion_values['Description'] = meta['Description']
            descripcion_values['Category'] = meta['Category']
            descripcion_values['Code'] = meta['Code']
        

        
        # Distinct values varible from dataset
        for db in data_values:
            descripcion_values['values'].append(db)



        collection = json.loads(json_util.dumps(descripcion_values))

        return jsonify(collection)

@ns_bigdatamed.doc(description="Clustering KMeans")
@ns_bigdatamed.route('/<name>/clustering/kmeans',methods=['POST'])
class kmeans(Resource):

  
  def post(self,name):
    
    # Obtener el dataframe que le pasamos por el request_session y los parámetros a través del formulario Config
    
    Object_Data = getData(name)
    X = Object_Data.get(name)
    
    object_json = json.loads(X.data)
    df = pd.DataFrame(object_json)

    
    config = json.loads(request.json)
   
    # Object_Clustering = clustering.ClusteringUnsupervised(columns=['HOSPITAL','AMBITO','IDENTIF','REGFIN',
    # 'TIPCIP','HISTORIAmodificada','TXTFECNAC','SEXO','RESIDE','MUNIRESI','PAISNAC','PROCEDE','HPROCEDE','TIPVISITA',
    # 'TIPING','SERVING','UCI','DIASUCI','TIPALT','TRASH','CONTINUIDA','SERVALT','UGCALT','C1','C2','C3','C4','C5','C6',
    # 'C7','C8','C9','C10','EDAD','TIEMPOING','MES','ESTACION','ANO'])

    # Object Clustering  in experimentation 
    # Aquí tendremos que obtener  [ columns = request.session variable recibidas en el config ]
    Object_Clustering = clustering.ClusteringUnsupervised(columns=['SERVING','EDAD'])
    
    object_data,labels = Object_Clustering.Kmeans(df,config['config'])
    labels = json.dumps( labels.tolist() )
    object_data['labels'] = labels
   
    return jsonify(object_data)

@ns_bigdatamed.doc(description="Obtención de datos filtrados")
@ns_bigdatamed.route('/<name>/filteredData', methods=['POST'])
class getFilteredData(Resource):
 
    def post(self, name):
        
        # Get the information from the request: filter of categorical variables, intervals and variables' names
        filter_categories_dict = request.json["filter_categories_dict"]
        filter_intervals_dict = request.json["filter_intervals_dict"]
        selected_variables = request.json["selected_variables"]

        if (len(filter_categories_dict) > 0):

            # convert the info from the request into mongodb query based string (categorical filter) *CHECK FOR CAT NULL VALUES, NOT INCLUDED*
            filter_categories_mongo_dict = {}
            for key in filter_categories_dict.keys():
                filter_categories_mongo_dict[key] = {'$in': [k for k, v in filter_categories_dict[key].items() if v]}

            # add the interval if needed
            filter_interval_mongo = ","

        else:

            # empty string because there is no categories
            filter_interval_mongo = ""

        # convert the info from the request into mongodb query based string (numerical/interval filter)
        if (len(filter_intervals_dict) > 0):
            filter_interval_mongo += "'$and': ["
            for key, value in filter_intervals_dict.items():
                filter_interval_mongo += "{'$or':["
                for value_interval in value.values():
                    filter_interval_mongo += "{'" + key + "':" + "{'$gte':" + str(value_interval[0]) + ", '$lte':" + str(value_interval[1]) + "}},"
                filter_interval_mongo += "]},"
            filter_interval_mongo += "]"

        # build and complete the main filter string

        if (len(filter_categories_dict) > 0 and len(filter_intervals_dict) > 0):
            # get the string with both filters
            filter_mongo_string = "{" + str(filter_categories_mongo_dict)[1:-1] + filter_interval_mongo + "}"

        elif (len(filter_categories_dict) > 0):
            # only categories filter
            filter_mongo_string = str(filter_categories_mongo_dict)

        else:
            # only interval filter
            filter_mongo_string = "{" + filter_interval_mongo + "}"

        # build the selected variables dictionary so mongo can do the selection
        selected_variables_dict = {}
        for var in selected_variables:
            selected_variables_dict[var] = 1

        # call the database to get the filtered data
        DB = dbases.database()
        data = DB.get_filtered_data(name, filter_mongo_string, selected_variables_dict)
        
        # transform data into json and send it back to the app
        data_json = json.loads(json_util.dumps(data))

        return data_json



