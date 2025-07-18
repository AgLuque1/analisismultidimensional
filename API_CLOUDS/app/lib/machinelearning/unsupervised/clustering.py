from sklearn.cluster import KMeans
import pandas as pd

# sklearn.cluster.KMeans(n_clusters=8, *, init='k-means++', n_init=10, 
# max_iter=300, tol=0.0001, verbose=0, random_state=None, copy_x=True, 
# algorithm='auto'
class ClusteringUnsupervised:
    
    # def Kmeans(n_clusters,init, n_init, max_iter,tol, verbose, random_state, copy_x, algorithm):
    def __init__(self,columns):
        self.list_columns = columns

    def use_columns_dataframe(self,df,list_columns):
        return df[list_columns]
    
   
    def Kmeans(self,df,config):
                
        if len(self.list_columns) > 0:
            df = self.use_columns_dataframe(df, self.list_columns)
                    
        # IMPORTANT: convert all categorical columns to numeric
        cat_columns = df.select_dtypes(['object']).columns
        df[cat_columns] = df[cat_columns].apply(lambda x: pd.factorize(x)[0])
        df.fillna(1,inplace=True)
        

        # TRANSFORM: dataframe in numpy array
        X = df.to_numpy()
        
        # PARAMS FOR KMEANS FORM INTERFACE
        n_clusters   = int(config['n_clusters'])
        init         = config['init']
        n_init       = int(config['n_init'])
        max_iter     = int(config['max_iter'])
        tol          = float(config['tol'])
        random_state = int(config['random_state'])
        algorithm    = config['algorithm']

        if config['verbose'] == 'on': verbose = 1
        else: verbose = 0

        if config['copy_x'] == 'on': copy_x = 1
        else: copy_x = 0
        
        # EXECUTE: KMean with params 
        kmeans = KMeans(n_clusters=n_clusters,init=init, n_init=n_init,max_iter=max_iter,tol=tol,
        verbose=verbose, random_state=random_state,copy_x=copy_x, algorithm=algorithm)                   
    
        # PREDICT: Clustering
        labels = kmeans.fit_predict(X)
       

        response = {'dataframe':df.to_json(orient='records')}
               

        return response,labels






        


