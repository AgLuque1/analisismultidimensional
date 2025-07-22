import pymongo
from pymongo import MongoClient

mongoServerConnection = "localhost:27017"
class database:
    #Function that get all name database allow access user. 
    def list_name_database(self):
        dbs = MongoClient( mongoServerConnection).list_database_names()
        return dbs

    #Function that get first 50 elements from database.
    def get_data(self, dbName):
        client = MongoClient( mongoServerConnection)
        
        db = client[dbName]
        collection = db['data']
        #cursor = collection.find({}).limit(5)
        cursor = collection.find({})
        return cursor
    
    #Function that get columns from database.
    def get_meta(self, dbName):
        client = MongoClient( mongoServerConnection)
        
        db = client[dbName]
        collection = db['meta']
        cursor = collection.find({},{'_id':False})
        return cursor

    # Function that get metadata variables columns from database.
    def get_meta_variable(self, dbName, variable):
        """_Values meta varibale selection_

        Args:
            dbName (_string_): Database name.
            variable (_string_): Column name.

        Returns:
           _cursor_: _Rows Database selection_
        """
        client = MongoClient( mongoServerConnection)
        
        db = client[dbName]
        collection = db['meta']
        
        cursor = collection.find({'Code':variable},
                                 {'Code':1,'Description':1,
                                  'VarType':1,'Category':1, 
                                  'DescriptionDetailed':1,
                                  '_id':False}
                                )
        
        return cursor

    # Function that get values columns from database.
    def get_values_variable(self, dbName,variable):
        """_Get rows depend of the type variable selection_

        Args:
            dbName (_string_): Database name.
            variable (_string_): Column name.

        Returns:
            _cursor_: _Rows Database selection_
        """
        
        client = MongoClient( mongoServerConnection)
        
        db = client[dbName]
        collection = db['data']        
        
        var_type = self.getTypeVariable(dbName,variable)
        
        if var_type=="Categorical":
            cursor = collection.distinct(variable)
        
        elif var_type=="Numerical":
            cursor = self.get_max_min(dbName,variable)
        
        else:
            cursor = []
        
        return cursor
        
    def getTypeVariable(self,dbName,variable):
        """_Get Variable Type of column selected_

        Args:
            dbName (_string_): Database name.
            variable (_string_): Column name.
        Returns:
            _string_: Variable type: Categorical, Numerical, Identificador
        """
        client = MongoClient( mongoServerConnection)
        
        db = client[dbName]
        collection = db['meta']
        
        cursor = collection.find({'Code':variable},{'VarType':1,'_id':False})
                
        var_type = [ elem['VarType']  for elem in cursor ][0]
       
        return var_type
        
        
    # Function that gets the count of each category of a categorical variable
    def get_count(self, dbName, dbField):
        client = MongoClient( mongoServerConnection)
        db = client[dbName]
        cursor = db['data'].aggregate([
            {
                '$group': {
                    '_id': '$' + dbField, 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ])
        return cursor

    # Function that gets all the documents of the data collection of the chosen database
    def get_number_documents(self, dbName):

        client = MongoClient( mongoServerConnection)
        db = client[dbName]

        return db['data'].count_documents({})

    # Function that gets the number of documents whose "dbField" field is not null
    def get_number_documents_var_not_null(self, dbName, dbField):

        client = MongoClient( mongoServerConnection)
        db = client[dbName]

        cursor = db['data'].aggregate([
            { "$group": {
                "_id": None,
                "numbernotnull": { "$sum": {"$cond": [{"$eq": ["$" + dbField, None]}, 0, 1] } },
                }
            }])

        return cursor

    # Function that gets the maximum and minimum value of a numerical field of the data collection of the database
    def get_max_min(self, dbName, dbField):

        client = MongoClient( mongoServerConnection)
        db = client[dbName]

        # get maximum and minimun value of a numeric variable
        cursor = db['data'].aggregate([
            { "$group": { 
                "_id": None,
                "max": { "$max": "$" + dbField }, 
                "min": { "$min": "$" + dbField } 
            }}])

        return cursor

    # Function that gets the type of the not null values of a field
    def get_type_not_null(self, dbName, dbField):

        client = MongoClient( mongoServerConnection)
        db = client[dbName]

        cursor = db['data'].aggregate( 
            [ 
                { "$match": {dbField:{"$ne":None}}},
                { "$project": { "fieldType": {  "$type": "$" + dbField  } } } 
            ]
        )

        return cursor

    # Function that gets the documents considering the variable dbField into groups, called buckets.
    # It gets the number of elements that belongs to each interval of the histogram. These boundaries are defined in the bins parameter
    def get_histogram(self, dbName, dbField, bins):

        client = MongoClient( mongoServerConnection)
        db = client[dbName]

        cursor = db['data'].aggregate([
            { "$match": {dbField:{"$ne":None}}},
            {
                '$bucket': {
                    'groupBy': "$" + dbField,
                    'boundaries': bins,
                    'default': "Other"
                }
            }
        ])

        return cursor

    # Function that gets the verbose name of the databases that the standard user can access
    def get_UserDBVerbose(self):

        client = MongoClient( mongoServerConnection)
        filter={
            'owner': 'user'
        }
        project={
            'dataset': 1, 
            'verbose': 1,
            '_id':0
        }

        result = client['MetaInformation']['data'].find(filter=filter, projection=project)

        return result

    # Function that gets the verbose name of the databases that an admin of the system can access
    def get_AdminDBVerbose(self):

        client = MongoClient( mongoServerConnection)
        filter={
            "$or": [
                    {"owner":"user"},
                    {"owner":"admin"}
            ]
        }
        project={
            'dataset': 1, 
            'verbose': 1,
            '_id':0
        }

        result = client['MetaInformation']['data'].find(projection=project)

        return result

    #Function that gets data based on the filter that gets as parameter
    def get_filtered_data(self, dbName, filterCategoriesIntervals, selected_variables_dict):

        client = MongoClient( mongoServerConnection)  
        db = client[dbName]
        collection = db['data']

        # run the filter string converted into a expression to get the cursor
        cursor = collection.find(eval(filterCategoriesIntervals), selected_variables_dict)

        return cursor
