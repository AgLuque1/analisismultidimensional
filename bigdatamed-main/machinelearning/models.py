# from djongo import models as djongomodels # se usa djongo para los modelos de datos, para poder utilizar las herramientas de djongo y pymongo (objects = models.DjongoManager()). Los modelos creados con djongo models no pueden usarse desde el admin debido a un bug con el id.
from django.utils.timezone import now
from django import forms

# Standard django models
from django.db import models # modelos estándar de django en este caso, pueden usarse y registrarse en el apartado de admin de django sin problema
from ckeditor.fields import RichTextField
from django.db.models.fields.files import ImageField

# import models from other app
from django.apps import apps

# Djongo approach

# model for testing multiclass classification - With djongo it uses _id
# class Iris(djongomodels.Model):
#     _id = djongomodels.ObjectIdField()
#     sepalLength = djongomodels.FloatField(default=None, blank=True, null=True)
#     sepalWidth = djongomodels.FloatField(default=None, blank=True, null=True)
#     petalLength = djongomodels.FloatField(default=None, blank=True, null=True)
#     petalWidth = djongomodels.FloatField(default=None, blank=True, null=True)
#     variety = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
    
#     objects = djongomodels.DjongoManager()

# # model for testing binary classification
# class Bank(djongomodels.Model):
#     _id = djongomodels.ObjectIdField()
#     age = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     job = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     marital = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     education = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     default = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     balance = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     housing = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     loan = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     contact = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     day = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     month = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     duration = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     campaign = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     pdays = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     previous = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     poutcome = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     deposit = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
    
#     objects = djongomodels.DjongoManager()

# # model for testing regression
# class MedicalCost(djongomodels.Model):
#     _id = djongomodels.ObjectIdField()
#     age = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     sex = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     bmi = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     children = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     smoker = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     region = djongomodels.CharField(max_length=200, default=None, blank=True, null=True)
#     charges = djongomodels.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     objects = djongomodels.DjongoManager()

# ################ Models for saving algorithm's initial configuration and results in a database - with django an automatic id integer field is created ################
    
# class BinaryLogisticRegressionResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxIter = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     coeffImage = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     rocImage = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     prImage = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class BinaryDecisionTreeResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage0 = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage1 = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class BinaryRandomForestResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
#     subsamplingRate = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     featureSubsetStrategy = models.CharField(max_length=200, default=None, blank=True, null=True)
#     numTrees = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     bootstrap = models.BooleanField(default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage0 = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage1 = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class BinaryGBTResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
#     subsamplingRate = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     featureSubsetStrategy = models.CharField(max_length=200, default=None, blank=True, null=True)
#     maxIter = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     lossType = models.CharField(max_length=200, default=None, blank=True, null=True)
#     validationTol = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     stepSize = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minWeightFractionPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
# class BinaryNaiveBayesResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     smoothing = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     modelType = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage0 = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rocImage1 = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class BinaryLinearSVCResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     aggregationDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxIter = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     regParam = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     standardization = models.BooleanField(default=None, blank=True, null=True)
#     tol = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     aucMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     aucBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     precisionBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score0 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrBest1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1Score1 = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)

# class MulticlassLogisticRegressionResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxIter = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     f1Mean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     coeffMatrix = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     f1ByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     fprByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     tprByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     precisionByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     recallByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     f1Weighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tprWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
# class MulticlassDecisionTreeResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     f1Mean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     f1ByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     fprByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     tnrByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     precisionByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     recallByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     f1Weighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
# class MulticlassRandomForestResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
#     subsamplingRate = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     featureSubsetStrategy = models.CharField(max_length=200, default=None, blank=True, null=True)
#     numTrees = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     bootstrap = models.BooleanField(default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     f1Mean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     f1ByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     fprByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     tnrByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     precisionByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     recallByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     f1Weighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)

# class MulticlassNaiveBayesResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     smoothing = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     modelType = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     labelMapping = models.CharField(max_length=1000, default=None, blank=True, null=True)
#     f1Mean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     accuracyBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     cmBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     cmNormBest = models.CharField(max_length=100000, default=None, blank=True, null=True)
#     f1ByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     fprByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     tnrByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     precisionByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     recallByLabel = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     f1Weighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     fprWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     tnrWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     precisionWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     recallWeighted = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
# class DecisionTreeRegressionResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     rmseMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mapeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rmseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     r2Best = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     regressionPlot = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class RandomForestRegressionResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
#     subsamplingRate = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numTrees = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     featureSubsetStrategy = models.CharField(max_length=200, default=None, blank=True, null=True)
#     bootstrap = models.BooleanField(default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     rmseMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mapeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rmseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     r2Best = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True) 
#     regressionPlot = models.CharField(max_length=100000, default=None, blank=True, null=True)
    
# class GBTRegressionResult(models.Model):
    
#     # Automatic Datetime - It will be set to the time the instance is first created
#     dateOfCreation = models.DateTimeField(default=now, editable=False)
    
#     # name of the model
#     model = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Execution time
#     executionTime = models.CharField(max_length=1000, default=None, blank=True, null=True)
    
#     # Algorithm Parameters
#     maxDepth = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxBins = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInstancesPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minInfoGain = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maxMemoryInMB = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     impurity = models.CharField(max_length=200, default=None, blank=True, null=True)
#     subsamplingRate = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     featureSubsetStrategy = models.CharField(max_length=200, default=None, blank=True, null=True)
#     maxIter = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     lossType = models.CharField(max_length=200, default=None, blank=True, null=True)
#     validationTol = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     stepSize = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     minWeightFractionPerNode = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     parallelism = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     numFolds = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
    
#     # Dataframe Schema
#     dfSchema = models.CharField(max_length=20000, default=None, blank=True, null=True)
#     dfShow = models.CharField(max_length=40000, default=None, blank=True, null=True)
#     dfShape = models.CharField(max_length=200, default=None, blank=True, null=True)
    
#     # Algorithm Results
#     rmseMean = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     maeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mapeBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     mseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     rmseBest = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     r2Best = models.DecimalField(max_digits=20, decimal_places=5, default=None, blank=True, null=True)
#     # regressionPlot = models.CharField(max_length=100000, default=None, blank=True, null=True)

    
# # model of subset configurations
# class SubsetConfig(models.Model):

#     qFilter = models.CharField(max_length=2000, default=None, blank=True, null=True)
#     verboseFilter = models.CharField(max_length=2000, default=None, blank=True, null=True)
#     selectedVariables = models.CharField(max_length=2000, default=None, blank=True, null=True)
#     relatedModel = models.CharField(max_length=2000, default=None, blank=True, null=True)
#     name = models.CharField(max_length=20, default=None, blank=True, null=True)
#     description = models.CharField(max_length=50, default=None, blank=True, null=True)
    