# Python standard useful libraries
import pandas as pd
from io import StringIO
import numpy as np

# Eda and Statistics
import seaborn as sns
import missingno as msno
import statistics
import statsmodels.api as sm
from scipy import stats

# Plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

# Custom Functions
from . import stringfunctions # for getting images and string manipulation
from . import plotfunctions

# forms used
from ..forms import *

"""
Function that manages univariate eda - calls the rest of functions

Parameters:

model: variable of the model
eda_variable: name of the variable that is going to be used in the univariate eda
data_list: rows of the variable, data
numeric: boolean, is it univariate numeric analysis or not.

Return:

univariate_dict: Returns a dictionary with unvariate numerical or categorical EDA accordingly.
It also contains variable with information about the form, model and parameters used and showed in the associated template.
The dictionary will contain the return values of the following functions:
- univariate_numeric: missing values, central tendency and dispersion measures, QQplot, skewness and kurtosis tests, histogram and boxplot.
- univariate_categorical: Returns a dictionary with unvariate categorical Statistics and images: missing values, absoute and relative frequencies and bar plot.

"""
def univariate_eda(model, eda_variable, data_list, numeric):
    
    # Get the rest of variables to use them as parameter for the bivariate analysis
    fields_ini = model._meta.fields
    fields = []

    for variable in fields_ini:
        position = stringfunctions.find_nth(str(variable), '.', 2)
        var_name = str(variable)[position+1:]

        if (str(eda_variable) != var_name):
            fields.append((var_name,var_name))

    # create the form for the bivariate analysis
    form = EdaBivariableForm()
    form.select_eda_variable(fields)

    # Univariate numeric analysis
    if numeric:

        # Call the univariate numeric analysis function and store all the variables correctly
        univariate_numeric_dict = univariate_numeric(eda_variable, data_list, False, '')
        
        # Add the type of analysis to the output dictionary
        univariate_dict = univariate_numeric_dict
        univariate_dict['analysis_type'] = 'numerical'

    # Univariate categorical analysis
    else:                

        # Call the univariate categorical analysis function and store all the variables correctly
        univariate_categorical_dict = univariate_categorical(eda_variable, data_list)
        
        # Calculate frequencies
        frequencies = pd.DataFrame()
        frequencies["Tipos"] =  list(univariate_categorical_dict['frequencies_absolute'].keys())
        frequencies["Absoluta"] =  list(univariate_categorical_dict['frequencies_absolute'].values())
        frequencies["Relativa"] =  list(univariate_categorical_dict['frequencies_relative'].values())
        
        # Add the type of analysis to the output dictionary
        univariate_dict = univariate_categorical_dict
        univariate_dict['analysis_type'] = 'categorical'
        univariate_dict['frequencies'] = frequencies

    # Complete the dictionary with some other relevant values
    univariate_dict['form'] = form
    univariate_dict['eda_variable'] = eda_variable
    univariate_dict['model'] = str(model)
    
    return univariate_dict

"""
Function that runs the Univariate numerical analysis

Parameters:

eda_variable: name of the variable that is going to be used in the univariate eda
data_list: rows of the variable, data
bivariate: boolean, is it bivariate analysis or not. This function is also used in bivariate numerical-categorical
cat_var: Contains the name of the categorical variable in numerical-categorical eda. For building titles of plots. 

Return:

univariate_numeric_dict: Returns a dictionary with unvariate numerical Statistics and images: missing values, central tendency and dispersion measures,
QQplot, skewness and kurtosis tests, histogram and boxplot.
"""
def univariate_numeric(eda_variable, data_list, bivariate, cat_var):
    
    #dictionary that contains the return values
    univariate_numeric_dict = {}
    
    #missing values

    # get the missing values
    eda_variable_list = []
    eda_variable_list.append(eda_variable)
    missing_values = pd.DataFrame(data_list,columns=eda_variable_list)

    # set size
    figure(figsize=(8, 8), dpi=80)

    # get the image of the missing values
    univariate_numeric_dict["missing_values_image"] = plotfunctions.plot_ml("missingValues", {"data": missing_values})

    # central tendency measures - measures of central location
    univariate_numeric_dict["mean"] = statistics.mean(data_list)
    univariate_numeric_dict["median"] = statistics.median(data_list)
    univariate_numeric_dict["mode"] = statistics.mode(data_list)

    univariate_numeric_dict["quantiles"] = ''
    if (len(data_list) > 1): # Check that data is bigger than 1
        univariate_numeric_dict["quantiles"] = statistics.quantiles(data_list)

    # measures of spread 
    univariate_numeric_dict["stdev"] = ''
    univariate_numeric_dict["variance"] = ''
    univariate_numeric_dict["IQR"] = ''
    if (len(data_list) > 1): # Check that data is bigger than 1
        univariate_numeric_dict["stdev"] = statistics.stdev(data_list)
        univariate_numeric_dict["variance"] = statistics.variance(data_list)
        univariate_numeric_dict["IQR"] = univariate_numeric_dict["quantiles"][2]-univariate_numeric_dict["quantiles"][0]

    univariate_numeric_dict["max_value"] = max(data_list)
    univariate_numeric_dict["min_value"] = min(data_list)
    univariate_numeric_dict["range"] = univariate_numeric_dict["max_value"]-univariate_numeric_dict["min_value"]

    # QQplot
    univariate_numeric_dict["QQplot_image"] = plotfunctions.plot_ml("qqPlot", {"data":data_list, "line":"s"})

    # Anderson-Darling test - Normality test
    univariate_numeric_dict["sw_test"] = ''
    if (len(data_list) > 2): # Check that data is bigger than 2
        univariate_numeric_dict["sw_test"] = stats.anderson(data_list, dist='norm')

    # Skewness and Kurtosis
    univariate_numeric_dict["skewness_test"] = stats.skew(data_list)
    univariate_numeric_dict["kurtosis_test"] = stats.kurtosis(data_list)

    # return all the useful local variables (tuple format)
    
    if (bivariate == False):
        
        # histogram
        univariate_numeric_dict["histogram"] = plotfunctions.plot_ml("histogram", {"data": data_list, "title": "Histograma - valor de la variable catégorica " + eda_variable})
        
        #boxplot
        univariate_numeric_dict["box_plot_image"] = plotfunctions.plot_ml("boxPlot", {"data": data_list, "title": "Boxplot con el valor de la variable catégorica " + eda_variable})
        
        
    else:

        # boxplot
        univariate_numeric_dict["box_plot_image"] = plotfunctions.plot_ml("boxPlot", {"data": data_list, "title": "Boxplot con el valor de la variable catégorica " + str(cat_var)})
        
        # histogram
        univariate_numeric_dict["histogram"] = plotfunctions.plot_ml("histogram", {"data": data_list, "title": "Histograma - valor de la variable catégorica " + str(cat_var)})
    
    return univariate_numeric_dict

"""
Function that runs the Univariate categorical analysis

Parameters:

eda_variable: name of the variable that is going to be used in the univariate eda
data_list: rows of the variable, data values

Return:

univariate_categorical_dict: Returns a dictionary with unvariate categorical Statistics and images: missing values, absoute and relative frequencies and
bar plot.
"""
def univariate_categorical(eda_variable, data_list):
    
    #dictionary that contains the return values
    univariate_categorical_dict = {}
        
    # set size
    figure(figsize=(8, 8), dpi=80)

    #missing values
    
    # get the missing values
    eda_variable_list = []
    eda_variable_list.append(eda_variable)
    missing_values = pd.DataFrame(data_list,columns=eda_variable_list)
    
    # get the image of the missing values
    univariate_categorical_dict["missing_values_image"] = plotfunctions.plot_ml("missingValues", {"data": missing_values})

    #bar plot - could be replaced or add a sector plot
    univariate_categorical_dict["bar_plot_image"] = plotfunctions.plot_ml("barPlot", {"data": data_list, 
                                                                                      "title": "Diagrama de barras con las frecuencias absolutas de la variable "+eda_variable})

    # frequency tables
    univariate_categorical_dict["frequencies_absolute"] = (pd.Series(data_list).value_counts()).to_dict()
    univariate_categorical_dict["frequencies_relative"] = ((pd.Series(data_list).value_counts())/len(data_list)).to_dict()
    
    return univariate_categorical_dict

"""
Function that runs the Bivariate eda analysis - calls the rest of functions

Parameters:

model: variable of the model
eda_variable: name of the first variable that is going to be used in the bivariate eda
eda_variable2: name of the second variable that is going to be used in the bivariate eda
data_list: rows of the first variable, data
numeric: boolean, if the first eda variable is numerical or not

Return:

bivariate_dict: Returns a dictionary with bivariate numerical/numerical, numerical/categorical or categorical/categorical EDA accordingly. Depending on the function it calls:

- bivariate_numeric_dict: Returns a dictionary with bivariate numerical Statistics and images: Scatterplot and Pearson coefficient.
- bivariate_categorical: Returns a dictionary with bivariate categorical Statistics and images: Crosstab, chi-squared coefficient and barplot filtered by each category
- bivariate_numeric_categorical: Returns a dictionary with a list associated to a univariate numerical analysis (Statistics and images: missing values,
central tendency and dispersion measures, QQplot, skewness and kurtosis tests, histogram and boxplot.) but filtered by every single value of the
categorical variable or category 

It also contains variables with information about the form, model and parameters used and showed in the associated template.
"""
def bivariate_eda(model, eda_variable, eda_variable2, data_list, numeric):
    
    # get columns of data from the database
    data = model.objects.values_list(eda_variable)
    data2 = model.objects.values_list(eda_variable2)

    # declare the list where the secon column values will be at
    data_list2 = []

    # Check if this second variable is numerical or categorical
    numeric2 = False
    
    if (model._meta.get_field(eda_variable2).get_internal_type() == "DecimalField"):
            numeric2 = True

    # 3 different possibilities

    # Both numerical
    if (numeric and numeric2):

        # Build the list with the second numerical column of data
        for element in data2:
                data_list2.append(float(element[0]))


        # Call the bivariate numerical-numerical analysis function and store all the variables correctly
        bivariate_dict = bivariate_numeric(data_list, data_list2, eda_variable, eda_variable2)
        
        # Add the type of analysis to the output dictionary
        bivariate_dict['analysis_type'] = 'numerical/numerical'
        
    # Numerical and categorical 
    elif ((not(numeric) and numeric2) or (numeric and not(numeric2))):

        #  Call the bivariate numerical-categorical analysis function and store all the variables correctly  
        bivariate_dict = bivariate_numeric_categorical(eda_variable, eda_variable2, numeric, numeric2, data, data2, model)

        # Add the type of analysis to the output dictionary
        bivariate_dict['analysis_type'] = 'numerical/categorical'

    # Both categorical
    else:

        # Build the list with the second categorical column of data
        for element2 in data2:
            data_list2.append(str(element2[0]))

        # Call the bivariate categorical-categorical analysis function and store all the variables correctly
        bivariate_dict = bivariate_categorical(data_list, data_list2, eda_variable, eda_variable2)

        # Add the type of analysis to the output dictionary
        bivariate_dict['analysis_type'] = 'categorical/categorical'
    
    # Complete the dictionary with some other relevant values
    bivariate_dict['eda_variable'] = eda_variable
    bivariate_dict['eda_variable2'] = eda_variable2
    bivariate_dict['model'] = str(model)
    
    return bivariate_dict


"""
Function that runs Bivariate numerical-numerical analysis

Parameters:

data_list: rows of the first variable, data values
data_list2: rows of the second variable, data values 
eda_variable: String with the name of the first eda variable. It will be used in the plots.
eda_variable2: String with the name of the second eda variable. It will be used in the plots.

Return:

bivariate_numeric_dict: Returns a dictionary with bivariate numerical Statistics and images: Scatterplot and Pearson coefficient.
"""
def bivariate_numeric(data_list, data_list2, eda_variable, eda_variable2):
    
    #dictionary that contains the return values
    bivariate_numeric_dict = {}
    
    # set size
    figure(figsize=(8, 8), dpi=80)
    
    # Scatter plot with regression line
    bivariate_numeric_dict["scatter_plot"] = plotfunctions.plot_ml("scatterPlot", {"data": data_list, "data2": data_list2, "var": eda_variable, "var2": eda_variable2})

    # Correlation coefficient
    bivariate_numeric_dict["pearson_coeff"] = np.corrcoef(data_list, data_list2)
    
    return bivariate_numeric_dict

"""
Function that runs Bivariate categorical-categorical analysis

Parameters:

data_list: rows of the first variable, data values
data_list2: rows of the second variable, data values
eda_variable: String with the name of the first eda variable. It will be used in the plots.
eda_variable2: String with the name of the second eda variable. It will be used in the plots.

Return:

bivariate_categorical_dict: Returns a dictionary with bivariate categorical Statistics and images: Crosstab, chi-squared coefficient and 
barplot filtered by each category
"""
def bivariate_categorical(data_list, data_list2, eda_variable, eda_variable2):
    
    #dictionary that contains the return values
    bivariate_categorical_dict = {}
    
    # set size
    figure(figsize=(8, 8), dpi=80)
    
    # Contingency table
    data_crosstab = pd.crosstab(index=[data_list], columns=[data_list2], margins = False)
    bivariate_categorical_dict["data_crosstab_df"] = (pd.DataFrame(data_crosstab)).to_html

    # Pearson Chi-Squared
    bivariate_categorical_dict["chi2"] = stats.chi2_contingency(np.array(data_crosstab))

    # Bar plot of both variables in two dimensions with colours
    bivariate_categorical_dict["bar_plot_2cat_image"] = plotfunctions.plot_ml("barPlot2Cat", {"data": data_list, "data2": data_list2, 'var1': eda_variable, 'var2': eda_variable2})
    
    return bivariate_categorical_dict

"""
Function that runs the Bivariate numerical/categorical analysis

Parameters:

eda_variable: name of the first variable that is going to be used in the bivariate eda
eda_variable2: name of the second variable that is going to be used in the bivariate eda
numeric: Boolean that contains if the first variable is numeric or not
numeric2: Boolean that contains if the second variable is numeric or not
data: rows of the first variable, data values
data2: rows of the second variable, data values
model: Model linked with noth variables. Used for plots' titles

Return:

bivariate_numeric_categorical_dict: Returns a dictionary with a list associated to a univariate numerical analysis (Statistics and images: missing values,
central tendency and dispersion measures, QQplot, skewness and kurtosis tests, histogram and boxplot.) but filtered by every single value of the
categorical variable or category 
"""
def bivariate_numeric_categorical(eda_variable, eda_variable2, numeric, numeric2, data, data2, model):
    
    #dictionary that contains the return values
    bivariate_numeric_categorical_dict = {}
    
    # set size
    figure(figsize=(8, 8), dpi=80)
    
    # Filter by categorical value and get the most important measures in single variable numeric analysis
  
    # Get which is the numeric/categorical variable and the unique values of data
    if (not(numeric) and numeric2):
        var_numeric = eda_variable2
        var_categorical = eda_variable
        unique_var = np.unique(data)

    else:
        var_numeric = eda_variable
        var_categorical = eda_variable2
        unique_var = np.unique(data2)

    
    # Declare empty lists for the filtered data 
    histogram_list = []
    mean_list = []
    median_list = []
    mode_list = []
    quantiles_list = []
    stdev_list = []
    variance_list = []
    max_value_list = []
    min_value_list = []
    range_list = []
    IQR_list = []
    box_plot_list = []
    sw_list = []

    # Iterate over all unique values
    for cat_var in unique_var:
        
        # declare the numeric list 
        data_list_numeric = []

        # automatic filtering
        filter_kwargs = {
            "{}__contains".format(var_categorical): cat_var
        }
        data_numeric = model.objects.filter(**filter_kwargs).values_list(var_numeric)

        # build the numeric list 
        for element in data_numeric:
            data_list_numeric.append(float(element[0]))  
            
        univariate_dict = univariate_numeric(var_numeric, data_list_numeric, True, cat_var)

        # Fill the lists
        
        histogram_list.append(univariate_dict["histogram"])
        mean_list.append((cat_var,univariate_dict["mean"]))
        median_list.append((cat_var,univariate_dict["median"]))
        mode_list.append((cat_var,univariate_dict["mode"]))
        max_value_list.append((cat_var,univariate_dict["max_value"]))
        min_value_list.append((cat_var,univariate_dict["min_value"]))
        range_list.append((cat_var,univariate_dict["range"]))
        box_plot_list.append(univariate_dict["box_plot_image"])
        
        # Check if the results are valid and fill the lists
        if (len(data_numeric) > 1):
            quantiles_list.append((cat_var,univariate_dict["quantiles"]))
            stdev_list.append((cat_var,univariate_dict["stdev"]))
            variance_list.append((cat_var,univariate_dict["variance"]))
            IQR_list.append((cat_var,univariate_dict["IQR"]))

        if (len(data_numeric) > 2):
            sw_list.append((cat_var,univariate_dict["sw_test"]))
            
        # Fill the output dictionary
        bivariate_numeric_categorical_dict['histogram_list'] = histogram_list
        bivariate_numeric_categorical_dict['mean_list'] = mean_list
        bivariate_numeric_categorical_dict['median_list'] = median_list
        bivariate_numeric_categorical_dict['mode_list'] = mode_list
        bivariate_numeric_categorical_dict['quantiles_list'] = quantiles_list
        bivariate_numeric_categorical_dict['stdev_list'] = stdev_list
        bivariate_numeric_categorical_dict['variance_list'] = variance_list
        bivariate_numeric_categorical_dict['max_value_list'] = max_value_list
        bivariate_numeric_categorical_dict['min_value_list'] = min_value_list
        bivariate_numeric_categorical_dict['range_list'] = range_list
        bivariate_numeric_categorical_dict['IQR_list'] = IQR_list
        bivariate_numeric_categorical_dict['box_plot_list'] = box_plot_list
        bivariate_numeric_categorical_dict['sw_list'] = sw_list

    return bivariate_numeric_categorical_dict