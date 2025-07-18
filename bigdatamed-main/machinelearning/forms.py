from random import choice, choices
from tabnanny import verbose
from django import forms

# Forms for the model selection


MODEL_CHOICE_KMEANS =(
    ('k-means++','k-means++'),
    ('random','random'),
)

MODEL_CHOICE_AlGORITHM =(
    ('auto','auto'),
    ('full','full'),
    ('elkan','elkan')
)


class ClusteringKmeansUnsupervised(forms.Form):
    n_clusters     = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}),
                    required=True, 
                    label="n_clusters", 
                    initial=8,
                    help_text="The number of clusters to form as well as the number of centroids to generate.")
                    
    init           = forms.ChoiceField(required=True,  
                    widget=forms.Select(attrs={'class':'form-control'}),
                    choices= MODEL_CHOICE_KMEANS, 
                    label="init", 
                    initial="k-means++",
                    help_text="K-means algorithm to use. The classical EM-style algorithm is “full”. The “elkan” variation is more efficient on data with well-defined clusters")


    n_init         = forms.IntegerField(required=True, 
                    widget=forms.TextInput(attrs={'class':'form-control'}),
                    label="n_init", 
                    initial="10",
                    help_text="Number of time the k-means algorithm will be run with different centroid seeds. ")

    max_iter       = forms.IntegerField(required=True,
                    widget=forms.TextInput(attrs={'class':'form-control'}),
                    label="max_iter", 
                    initial="300",
                    help_text="Maximum number of iterations of the k-means algorithm for a single run.")

    tol            = forms.IntegerField(required=True, 
                    widget=forms.TextInput(attrs={'class':'form-control'}),
                    label="tol", 
                    initial="0.0001",
                    help_text="Relative tolerance with regards to Frobenius norm of the difference in the cluster centers of two consecutive iterations to declare convergence.")
    
    verbose        = forms.BooleanField(
                    label="verbose",
                    initial=False,
                    help_text="Verbosity mode.")
    
    random_state   = forms.IntegerField(required=True, 
                    widget=forms.TextInput(attrs={'class':'form-control'}),
                    label="random_state", 
                    initial=0,
                    help_text="Determines random number generation for centroid initialization.")

    copy_x         = forms.BooleanField(
                    label="copy_x",
                    initial=False,
                    help_text="If copy_x is True (default), then the original data is not modified. If False, the original data is modified, and put back before the function returns,")
    
    algorithm      = forms.ChoiceField(required=True,  
                    widget=forms.Select(attrs={'class':'form-control'}),
                    choices= MODEL_CHOICE_AlGORITHM, 
                    label="algorithm", 
                    initial="auto",
                    help_text="K-means algorithm to use. The classical EM-style algorithm is “full”. The “elkan” variation is more efficient on data with well-defined clusters")























MODEL_CHOICES = (
    ('Iris', 'Iris'),
    ('Bank', 'Bank'),
    ('MedicalCost', 'MedicalCost'),
)    

class ModelSelectionForm(forms.Form):
    model = forms.ChoiceField(required=False,  choices = MODEL_CHOICES)
    
class ModelSelectionFormChar(forms.Form):
    model = forms.CharField(required = True, max_length=1000)
    


# Forms for filtering variable in display data view

class VariableFilterForm(forms.Form):
    variable = forms.ChoiceField(required=False)
    operator = forms.ChoiceField(required=False,  choices = (
        ("Igual que", "Igual que"),
        ("Igual que (no sensible a mayus)", "Igual que (no sensible a mayus)"),
        ("Contiene", "Contiene"),
        ("Contiene (no sensible a mayus)", "Contiene (no sensible a mayus)"),
        ("Mayor que", "Mayor que"),
        ("Mayor o igual que", "Mayor o igual que"),
        ("Menor que", "Menor que"),
        ("Menor o igual que", "Menor o igual que"),
        ("Empieza por", "Empieza por"),
        ("Empieza por (no sensible a mayus)", "Empieza por (no sensible a mayus)"),
        ("Termina por", "Termina por"),
        ("Termina por (no sensible a mayus)", "Termina por (no sensible a mayus)"),
        ("Expresión regular", "Expresión regular"),
        ("Expresión regula (no sensible a mayus)r", "Expresión regular (no sensible a mayus)"),
        )
    )
    value = forms.CharField(required=False, max_length=1000)
    
    def create_variables(self, variable_choices, *args, **kwargs):
        super(VariableFilterForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices = variable_choices
        
class VariableFilterFormChar(forms.Form):
    variable = forms.CharField(required=False, max_length=1000)
    operator = forms.CharField(required=False, max_length=1000)
    value = forms.CharField(required=False, max_length=1000)

# Forms for selecting the EDA variables. The function initializes the choices based on model's variables
class EdaUnivariableForm(forms.Form):
    variable = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = True)
    
    def select_eda_variable(self, variable_choices, *args, **kwargs):
        super(EdaUnivariableForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices = variable_choices
        
class EdaBivariableForm(forms.Form):
    variable = forms.MultipleChoiceField(widget=forms.RadioSelect, required = True)
    
    def select_eda_variable(self, variable_choices, *args, **kwargs):
        super(EdaBivariableForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices = variable_choices
        
# Forms for selecting a binary classification algorithm
BINARY_ALGORITHM_CHOICES = (
    ('BinaryLogisticRegression', 'BinaryLogisticRegression'),
    ('BinaryDecisionTree', 'BinaryDecisionTree'),
    ('BinaryRandomForest', 'BinaryRandomForest'),
    ('BinaryGBT', 'BinaryGBT'),
    ('BinaryNaiveBayes', 'BinaryNaiveBayes'),
    ('BinaryLinearSVC', 'BinaryLinearSVC'),
)    
    
class BinaryClassificationAlgorithmSelectionForm(forms.Form):
    algorithm = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=BINARY_ALGORITHM_CHOICES, required = True)
    
class BinaryClassificationAlgorithmSelectionFormChar(forms.Form):
    algorithm = forms.CharField(required = True, max_length=1000)

# Forms for selecting a multiclass classification algorithm
MULTICLASS_ALGORITHM_CHOICES = (
    ('MulticlassLogisticRegression', 'MulticlassLogisticRegression'),
    ('MulticlassDecisionTree', 'MulticlassDecisionTree'),
    ('MulticlassRandomForest', 'MulticlassRandomForest'),
    ('MulticlassNaiveBayes', 'MulticlassNaiveBayes'),
)       
    
class MulticlassClassificationAlgorithmSelectionForm(forms.Form):
    algorithm = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=MULTICLASS_ALGORITHM_CHOICES, required = True)

class MulticlassClassificationAlgorithmSelectionFormChar(forms.Form):
    algorithm = forms.CharField(required = True, max_length=1000)

# Forms for selecting a regression algorithm
REGRESSION_ALGORITHM_CHOICES = (
    ('DecisionTreeRegression', 'DecisionTreeRegression'),
    ('RandomForestRegression', 'RandomForestRegression'),
    ('GBTRegression', 'GBTRegression'),
)       
    
class RegressionAlgorithmSelectionForm(forms.Form):
    algorithm = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=REGRESSION_ALGORITHM_CHOICES, required = True)

class RegressionAlgorithmSelectionFormChar(forms.Form):
    algorithm = forms.CharField(required = True, max_length=1000)
    
# Forms for selecting the input and output variables of models

# Iris Model
Iris_CHOICES = (
    ('varietyTarget', 'varietyTarget'),
)      
    
class IrisSelectionForm(forms.Form):
    sepalLength = forms.BooleanField(required = False, initial = True) 
    sepalWidth = forms.BooleanField(required = False, initial = True) 
    petalLength = forms.BooleanField(required = False, initial = True)
    petalWidth = forms.BooleanField(required = False, initial = True)
    variety = forms.BooleanField(required = False)
    
# Bank Model
Bank_CHOICES = (
    ('depositTarget', 'depositTarget'),
)      
    
class BankSelectionForm(forms.Form):
    age = forms.BooleanField(required = False, initial = True) 
    job = forms.BooleanField(required = False, initial = True) 
    marital = forms.BooleanField(required = False, initial = True) 
    education = forms.BooleanField(required = False, initial = True) 
    default = forms.BooleanField(required = False) 
    balance = forms.BooleanField(required = False) 
    housing = forms.BooleanField(required = False) 
    loan = forms.BooleanField(required = False) 
    contact = forms.BooleanField(required = False) 
    day = forms.BooleanField(required = False) 
    month = forms.BooleanField(required = False) 
    duration = forms.BooleanField(required = False) 
    campaign = forms.BooleanField(required = False) 
    pdays = forms.BooleanField(required = False) 
    previous = forms.BooleanField(required = False) 
    poutcome = forms.BooleanField(required = False) 
    deposit = forms.BooleanField(required = False) 
    
# MedicalCost Model
MedicalCost_CHOICES = (
    ('chargesTarget', 'chargesTarget'),
)      
    
class MedicalCostSelectionForm(forms.Form):
    age = forms.BooleanField(required = False, initial = True) 
    sex = forms.BooleanField(required = False, initial = True) 
    bmi = forms.BooleanField(required = False, initial = True) 
    children = forms.BooleanField(required = False, initial = True) 
    smoker = forms.BooleanField(required = False, initial = True) 
    region = forms.BooleanField(required = False, initial = True) 
    charges = forms.BooleanField(required = False) 

# Form for selecting the target variable
class TargetForm(forms.Form):
    target = forms.MultipleChoiceField(widget=forms.RadioSelect, required = True)
    
    def create_target(self, variable_choices, *args, **kwargs):
        super(TargetForm, self).__init__(*args, **kwargs)
        self.fields['target'].choices = variable_choices
        
class TargetFormChar(forms.Form):
    target = forms.CharField(required = True, max_length=1000)
    
# Form for cluster parameters set up
class ClusterSetUpForm(forms.Form):
    distributed = forms.BooleanField(required = False, initial = False)
    conexionToSparkMaster = forms.CharField(required=True, initial = 'spark://172.21.144.1:7077', max_length=1000)  
    numberOfCores = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numberOfCoresPerExecutor = forms.IntegerField(required=True, initial = 1, min_value = 1)
    executorMemory = forms.IntegerField(required=True, initial = 1, min_value = 1)
    
# Choices for algorithm variables
IMPURITY_DT_RF_CHOICES = [
    ('gini', 'gini'),
    ('entropy', 'entropy')
]

IMPURITY_GBT_CHOICES = [
    ('variance', 'variance')
]

LOSSTYPES_GBT_CHOICES = [
    ('logistic', 'logistic')
]

FSS_CHOICES = [
    ('auto', 'auto'),
    ('all', 'all'),
    ('onethird', 'onethird'),
    ('sqrt', 'sqrt'),
    ('log2', 'log2')
]

MODELTYPE_NAIVEBAYES_CHOICES = [
    ('multinomial ', 'multinomial '),
    ('bernoulli', 'bernoulli'),
    ('gaussian', 'gaussian')
]

IMPURITY_REGRESSION_CHOICES = [
    ('variance', 'variance')
]

LOSSTYPE_REGRESSION_CHOICES = [
    ('squared', 'squared'),
    ('absolute', 'absolute')
]

# Forms of classification algorithms
class LogisticRegressionForm(forms.Form):
    maxIter = forms.IntegerField(required=True, min_value = 0, initial = 100)
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, min_value = 1, initial = 10)
    
class DecisionTreeForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2)
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1)
    minInfoGain = forms.FloatField(required=True, initial = 0.0)
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256)
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_DT_RF_CHOICES)
    
class DecisionTreeFormChar(forms.Form):
    parallelism = forms.IntegerField(required=True)
    numFolds = forms.IntegerField(required=True)
    maxDepth = forms.IntegerField(required=True)
    maxBins = forms.IntegerField(required=True)
    minInstancesPerNode = forms.IntegerField(required=True)
    minInfoGain = forms.FloatField(required=True)
    maxMemoryInMB = forms.IntegerField(required=True)
    impurity = forms.CharField(required=True, max_length=1000)
    
class RandomForestForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2)
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1)
    minInfoGain = forms.FloatField(required=True, initial = 0.0)
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256)
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_DT_RF_CHOICES)
    subsamplingRate = forms.FloatField(required=True, initial = 1.0, min_value = 0.00000001, max_value = 1)
    featureSubsetStrategy = forms.ChoiceField(required=True,  choices = FSS_CHOICES)
    numTrees = forms.IntegerField(required=True, initial = 10, min_value = 1)
    bootstrap = forms.BooleanField(required = False, initial = True)
    
class RandomForestFormChar(forms.Form):
    parallelism = forms.IntegerField(required=True)
    numFolds = forms.IntegerField(required=True)
    maxDepth = forms.IntegerField(required=True)
    maxBins = forms.IntegerField(required=True)
    minInstancesPerNode = forms.IntegerField(required=True)
    minInfoGain = forms.FloatField(required=True)
    maxMemoryInMB = forms.IntegerField(required=True)
    impurity = forms.CharField(required=True, max_length=1000)
    subsamplingRate = forms.FloatField(required=True)
    featureSubsetStrategy = forms.CharField(required=True, max_length=1000)
    numTrees = forms.IntegerField(required=True)
    bootstrap = forms.BooleanField(required = True)
    
class GBTForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2)
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1)
    minInfoGain = forms.FloatField(required=True, initial = 0.0)
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256)
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_GBT_CHOICES)
    subsamplingRate = forms.FloatField(required=True, initial = 1.0, min_value = 0.00000001, max_value = 1) 
    featureSubsetStrategy = forms.ChoiceField(required=True,  choices = FSS_CHOICES)
    maxIter = forms.IntegerField(required=True, initial = 20, min_value = 0)
    lossType = forms.ChoiceField(required=True,  choices = LOSSTYPES_GBT_CHOICES)
    validationTol = forms.FloatField(required=True, initial = 0.01)
    stepSize = forms.FloatField(required=True, initial = 0.1, min_value = 0.00000001, max_value = 1)
    minWeightFractionPerNode = forms.FloatField(required=True, initial = 0.0, min_value = 0, max_value = 0.499999999)
    
class GBTFormChar(forms.Form):
    parallelism = forms.IntegerField(required=True)
    numFolds = forms.IntegerField(required=True)
    maxDepth = forms.IntegerField(required=True) 
    maxBins = forms.IntegerField(required=True) 
    minInstancesPerNode = forms.IntegerField(required=True) 
    minInfoGain = forms.FloatField(required=True) 
    maxMemoryInMB = forms.IntegerField(required=True) 
    impurity = forms.CharField(required=True, max_length=1000) 
    subsamplingRate = forms.FloatField(required=True) 
    featureSubsetStrategy = forms.CharField(required=True, max_length=1000) 
    maxIter = forms.IntegerField(required=True)
    lossType = forms.CharField(required=True, max_length=1000)
    validationTol = forms.FloatField(required=True)
    stepSize = forms.FloatField(required=True)
    minWeightFractionPerNode = forms.FloatField(required=True)
    
class NaiveBayesForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    smoothing = forms.FloatField(required=True, initial = 1.0, min_value = 0)
    modelType = forms.ChoiceField(required=True,  choices = MODELTYPE_NAIVEBAYES_CHOICES)
    
class NaiveBayesFormChar(forms.Form):
    parallelism = forms.IntegerField(required=True)
    numFolds = forms.IntegerField(required=True)
    smoothing = forms.FloatField(required=True)
    modelType = forms.CharField(required=True, max_length=1000)   

class LinearSVCForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    aggregationDepth = forms.IntegerField(required=True, initial = 2, min_value = 2)
    maxIter = forms.IntegerField(required=True, initial = 100, min_value = 0)
    regParam = forms.FloatField(required=True, initial = 0.0, min_value = 0.0)
    standardization = forms.BooleanField(required = False, initial = True)
    tol = forms.FloatField(required=True, initial = 0.000001, min_value = 0)

# Forms of regression algorithms
class DecisionTreeRegressionForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2)
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1)
    minInfoGain = forms.FloatField(required=True, initial = 0.0)
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256)
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_REGRESSION_CHOICES)
    
class RandomForestRegressionForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2)
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1)
    minInfoGain = forms.FloatField(required=True, initial = 0.0)
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256)
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_REGRESSION_CHOICES)
    subsamplingRate = forms.FloatField(required=True, initial = 1.0, min_value = 0.00000001, max_value = 1)
    featureSubsetStrategy = forms.ChoiceField(required=True,  choices = FSS_CHOICES)
    numTrees = forms.IntegerField(required=True, initial = 10, min_value = 1)
    bootstrap = forms.BooleanField(required = False, initial = True)
    
class GBTRegressionForm(forms.Form):
    parallelism = forms.IntegerField(required=True, initial = 8, min_value = 1)
    numFolds = forms.IntegerField(required=True, initial = 10, min_value = 1)
    maxDepth = forms.IntegerField(required=True, initial = 5, min_value = 0)
    maxBins = forms.IntegerField(required=True, initial = 32, min_value = 2) 
    minInstancesPerNode = forms.IntegerField(required=True, initial = 1, min_value = 1) 
    minInfoGain = forms.FloatField(required=True, initial = 0.0) 
    maxMemoryInMB = forms.IntegerField(required=True, initial = 256) 
    impurity = forms.ChoiceField(required=True,  choices = IMPURITY_REGRESSION_CHOICES)
    subsamplingRate = forms.FloatField(required=True, initial = 1.0, min_value = 0.00000001, max_value = 1) 
    featureSubsetStrategy = forms.ChoiceField(required=True,  choices = FSS_CHOICES)
    maxIter = forms.IntegerField(required=True, initial = 20, min_value = 0)
    lossType = forms.ChoiceField(required=True,  choices = LOSSTYPE_REGRESSION_CHOICES)
    validationTol = forms.FloatField(required=True, initial = 0.01)
    stepSize = forms.FloatField(required=True, initial = 0.1, min_value = 0.00000001, max_value = 1)
    minWeightFractionPerNode = forms.FloatField(required=True, initial = 0.0, min_value = 0, max_value = 0.499999999)
    
class CreateSubsetForm(forms.Form):    
    name = forms.CharField(required=False, max_length=20)
    description = forms.CharField(required=False, max_length=50)