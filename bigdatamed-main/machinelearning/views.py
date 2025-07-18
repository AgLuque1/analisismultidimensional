# Django imports - generics
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.conf import settings
#ML Models
from .models import *
import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE

import plotly.io as pio


# Dashboard Category model
from dashboard.models import Category

# Forms
from .forms import *

# Python standard useful libraries
# import pandas as pd
from io import StringIO
# import numpy as np
import sys
from contextlib import redirect_stdout
import os
import time

import requests
import json

# SQLAlchemy, for pandas to insert data in local SQL Database
# from sqlalchemy import create_engine

# Import of own functions from tools folder
# from .tools import stringfunctions # for getting images and string manipulation
# from .tools import eda # for exploratory data analysis and obtaining its plots
# from .tools import sparkpreprocessing # for spark algorithm's required preprocessing
# from .tools import algorithmsmanagement # for manage the set up of algorithms
# from .tools import filteringfunctions # tools for applying filters

# Eda and Statistics
# import seaborn as sns
# import missingno as msno
# import statistics
# import statsmodels.api as sm
# from scipy import stats

# # Plot
# import matplotlib.pyplot as plt

# Pyspark
# from pyspark import SparkContext, SparkConf
# from pyspark.sql import SparkSession

# # Debug
# import logging
# import ipdb

# # MongoDB
# import bson

# Index View of the app - shows links to app's main options and allows to do custom querys (this will be done using django tables)
@login_required
def home(request):
    url_service = settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + "/meta/"
    FormClusteringKmeansUnsupervised = ClusteringKmeansUnsupervised()

    return render(request, "home-machine-learning.html",locals())


@login_required
def result_execute_experiment(request):
    config ={}
    if request.POST:
        config['n_clusters']      = request.POST['n_clusters']
        config['init']            = request.POST['init']
        config['n_init']          = request.POST['n_init']
        config['max_iter']        = request.POST['max_iter']
        config['tol']             = request.POST['tol']
        config['verbose']         = request.POST['verbose']
        config['random_state']    = request.POST['random_state']
        config['copy_x']          = request.POST['copy_x']
        config['algorithm']      = request.POST['algorithm']

        data = { 'config': config, 'date_init':request.session['date_init'], 'date_end':request.session['date_end'] }
        
        # Call Service clustering means
        response = requests.post( settings.URL_CONFIG_API_REST +request.session['select_bbdd']+'/clustering/kmeans',json=json.dumps(data) )

        # CREATE Json for dataframe and labels
        dataframe= json.loads(response.json()["dataframe"])
        labels= json.loads(response.json()["labels"])

        # CREATE  DATAFRAME
        df = pd.DataFrame.from_dict(dataframe,orient='columns')
       
        # TSNE COMPONENTS --> PCA
        tsne = TSNE(n_components=2, random_state=0)
        projections = tsne.fit_transform(df)
       
        # ADD field clusters in dataframe
        df['clusters'] = labels
        fig = px.scatter(
            projections, x=0, y=1,
            color=df.clusters, labels={'color': 'CLUSTERS'}
        )
        
        # Create graph.html
        pio.write_html(fig, file=settings.MEDIA_ROOT + "/tmp/visualization/graph.html", auto_open=False)
        
    return render(request, "result-experiment.html",locals())

#     # Logger set up
#     logger = logging.getLogger('logger_machinelearning')
    
#     # Set up default model
#     if (not (request.session.get('model', None))):
#         request.session['model'] = "Iris"
#         chosen_model = "Iris"
#         model_string = "El modelo activo es (por defecto): "
#     else:
#         chosen_model = request.session['model']
#         model_string = "El modelo activo es: "

#     if ("GET" == request.method):
        
#         form = ModelSelectionForm()
                
#         return render(request, "ML_index.html", {'form': form, 'chosen_model':chosen_model, 'model_string':model_string})
    
#     # if not get, then POST 
#     else:
       
#         # create a form instance and populate it with data from the request:
#         form = ModelSelectionFormChar(request.POST)
        
#         # check whether it's valid:
#         if form.is_valid():
            
#             request.session['model'] = form.cleaned_data['model']
                    
#         return HttpResponseRedirect(reverse("machinelearning:ML_index"))
    
# # View to add patients to user's local SQL database
# @login_required
# def MLUploadCsvView(request):

#     model = globals()[request.session['model']]
    
#     if ("GET" == request.method):
#         return render(request, "ML_upload_csv.html",  {'model': request.session['model']})
    
#     # if not get, then POST 
#     else:
        
#         # get the file from the request
#         csv_file = request.FILES["csv_file"]
        
#         # check if .csv extension is correct
#         if not csv_file.name.endswith('.csv'):
#             return render(request, "ML_upload_csv.html", {'model': request.session['model'] , 'error_extension': True})
        
#         # set MAX SIZE
#         MAX_SIZE = 104857600
        
#         # check file length
#         if (csv_file.size > MAX_SIZE) :
#             return render(request, "ML_upload_csv.html", {'model': request.session['model'] , 'error_size': True})

#         # decode the file and build a dataframe from it
#         file_data = csv_file.read().decode("utf-8")
#         file_data_string = StringIO(file_data)
#         df = pd.read_csv(file_data_string, sep=';')
        
#         #MongoDB approach
                
#         model.objects.mongo_insert_many(df.to_dict('records'))
        
#         return HttpResponseRedirect(reverse("machinelearning:ML_index"))
    
# # View that manages the configuration of the dataset and the request to the database
# @login_required
# def MLDatasetConfigView(request):
    
#     # temporary model selection in this view
    
#     if ("GET" == request.method):
        
#         # build the form that will let the user use one of the available models/datasets
#         form = ModelSelectionForm()
                
#         # build the dictionary that will be used in template to show some of the variables: model, form and info about the active model
#         dataset_config_dict = {}
#         dataset_config_dict["model"] = request.session['model']
#         dataset_config_dict["form"] = form
        
#         # check if there is an active filter
#         if (request.session.get('subset_built', None)):
#             dataset_config_dict["subset_built"] = True
#             dataset_config_dict["filter_string_subset_verbose"] = request.session['filter_string_subset_verbose']
#             dataset_config_dict["variables_subset"] = request.session['variables_subset']
            
#         # get the previous subset configurations done by the user
#         dataset_config_dict["previous_configurations"] = SubsetConfig.objects.all().values("id", "name", "description", "verboseFilter", "selectedVariables", "relatedModel")
        
#         # build the view title
#         title_content = "Configuración del conjunto de datos"

#         return render(request, "ML_dataset_config.html", {"dataset_config_dict": dataset_config_dict, "title_content":title_content})
    
#     else:
        
#         form = ModelSelectionFormChar(request.POST)
#         if form.is_valid():
            
#             # select the new dataset or model
#             request.session['model'] = form.cleaned_data['model']
            
#             # clean the previous dataset information
#             if ((request.session.get('variables_subset', None))):
#                 del request.session['variables_subset']
            
#         return HttpResponseRedirect(reverse("machinelearning:ML_reset_filter", args=("dataset_config",)))
    
# # View that activates a previous defined subdataset configuration
# @login_required
# def MLActivatePreviousConfig(request, id_previous_config):
    
#     # get the info of the previous instance
#     instance = SubsetConfig.objects.filter(_id=bson.objectid.ObjectId(id_previous_config)).values()
    
#     # reset the previous filters and subsets variables
#     filteringfunctions.clear_filter(request)
#     filteringfunctions.clear_filter_subset(request)
    
#     # activate previous configuration
#     request.session['subset_built'] = True
#     request.session['filter_string_subset'] = instance[0]["qFilter"]
#     request.session['filter_string_subset_verbose'] = instance[0]["verboseFilter"]
#     request.session['variables_subset'] = eval(instance[0]["selectedVariables"])
#     request.session['name_subset'] = instance[0]["name"]
#     request.session['description_subset'] = instance[0]["description"]

#     return HttpResponseRedirect(reverse("machinelearning:ML_dataset_config"))
    
# # View that show cards, depending on the id of the parent category. id will be an integer or a "None", if it has no parent
# @login_required
# def MLShowCardsView(request, id_parent):
    
#     # select the categories whose parent is the correct one
#     categories = Category.objects.filter(parentcat__id=id_parent)
    
#     # get the parent name which will be the title of the view
#     title_content = categories[0].parentcat.name
    
#     # if parent's name is Exporar datos, knowledge discovery will be the next step in the WF
#     if (title_content == "Explorar datos"):
#         next_wf = "machinelearning:ML_show_cards"
#         next_wf_param = 5
        
#     elif (title_content == "Extracción de conocimiento"):
#         next_wf = "machinelearning:ML_previous_results"

#     return render(request, "ML_show_cards.html", locals())

# # Display of data in table shape
# @login_required
# def MLDisplayFilterDataView(request, order_variable):
    
#     model = globals()[request.session['model']]
    
#     if ("GET" == request.method):
    
#         # Dictionary that will contain all the information to display in the template
#         view_dict = {}        

#         # get the columns or variables that are going to be displayed. based on the variables that were selected in view MLSelectVariableView
#         variables_dict = filteringfunctions.get_dataset_variables(request, model)
        
#         # check if there is an active subset filter
    
#         # if subset_built session variable is set up to True, it means that we can't be setting up a subset. We have to be displaying data.
#         if (request.session.get('subset_built', None)):
            
#             # check if the subset filter is an empty value (there is no need to use the django filter function)
#             if (request.session['filter_string_subset'] == ""):
                
#                 data_filtered = model.objects.all()
                
#             else:

#                 data_filtered = model.objects.filter(eval(request.session['filter_string_subset']))
#                 view_dict["filter_string_subset_verbose"] = request.session['filter_string_subset_verbose'] # string that contains the filters that build the subset
#                 view_dict["subset_building"] = False # Subset has already been built
                
#             # build the title of the view (display data)
#             title_content = "Visualización de datos - Modelo " + request.session["model"]
        
#         # building a subset
#         else:
            
#             data_filtered = model.objects.all()
#             view_dict["subset_building"] = True # Subset is being built
            
#             # build the title of the view (build subset)
#             title_content = "Creación de subconjunto de datos - Modelo " + request.session["model"]
    
#         # check if there is an active filter in the view - Apply second filter
        
#         # if filtering is set up to true, filter the data with the new info and get its values (only with selected columns or variables). 
#         if (request.session.get('filtering', None)):
    
#             # check if the filter is an empty value (there is no need to use the django filter function)
#             if (request.session['filter_string'] == ""):

#                 data_filtered = data_filtered.values(*variables_dict["variable_names"])
                
#             else:
#                 data_filtered = data_filtered.filter(eval(request.session['filter_string'])).values(*variables_dict["variable_names"])
            
#         else:
            
#             data_filtered = data_filtered.values(*variables_dict["variable_names"])
        
#         # make the pagination process and sort the values
#         pagination_dict = filteringfunctions.run_pagination(request, data_filtered, order_variable)
        
#         # update the view dictionary with the values created by the pagination function: page, data, dictionary_list, current_order
#         view_dict.update(pagination_dict)
                    
#         # get the empty filter form
#         form = VariableFilterForm()
        
#         # create dynamic choices in the form from the selected variables
#         form.create_variables(variables_dict["variable_pairs_form"])
            
#         # fill the rest of output dictionary fields
        
#         view_dict["variable_names"] = variables_dict["variable_names"] # list with the name of variables
#         view_dict["form"] = form # form for filtering
#         view_dict["model"] = request.session['model'] # string with the name of the active model or name of the dataset
#         view_dict["order_variable"] = order_variable # variable that was used in row sorting
        
#         # if filter string is initialized (the user is building a string), add the fields to the output dictionary
#         if (request.session.get('filter_string', None)):
#             view_dict["filter_string"] = request.session['filter_string']
#             view_dict["filter_string_verbose"] = request.session['filter_string_verbose']
        
#         # If there is a filter ongoing in the view, , add the fields to the output dictionary
#         if (request.session.get('filtering', None)):
#             view_dict["filtering"] = request.session['filtering']
        
#         return render(request, "ML_display_filter_data.html", {'view_dict': view_dict, "title_content":title_content})
    
#     else:
                
#         # create a form instance and populate it with data from the request:
#         form = VariableFilterFormChar(request.POST)

#         # check whether it's valid:
#         if form.is_valid():  
            
#             # translate the operator of the form so Django can work with it (Igual que -> exact, etc.)
#             filteringfunctions.translate_operator(form)
            
#             # check the value of the field and transform it value if needed.
#             if (model._meta.get_field(form.cleaned_data['variable']).get_internal_type() == "FloatField"):
                
#                 # update the value of the filter on the new operation that is going to be added. Value float
#                 request.session['value_filter'] = float(form.cleaned_data['value'])
                
#             elif (model._meta.get_field(form.cleaned_data['variable']).get_internal_type() == "CharField"):
                
#                 # update the value of the filter on the new operation that is going to be added. Value char
#                 request.session['value_filter'] = "'" + form.cleaned_data['value'] + "'"
                
#             # update the variable and the operator of the filter on the new operation that is going to be added
#             request.session['variable_filter'] = form.cleaned_data['variable']
#             request.session['operator_filter'] = form.cleaned_data['operator']
            
#             return HttpResponseRedirect(reverse("machinelearning:ML_build_complex_filter", args=("add_operation",)))

# # Display of data in table shape
# @login_required
# def MLCreateSubsetView(request):
    
#     model = globals()[request.session['model']]
    
#     if ("GET" == request.method):
        
#         form = CreateSubsetForm()
#         title_content = "Introduzca el nombre y la descripción de la configuración del dataset que se va a crear"
        
#         return render(request, "ML_create_subset.html", locals())
    
#     else:
        
#         form = CreateSubsetForm(request.POST)
        
#         if (form.is_valid()):
#             request.session['name_subset'] = form.cleaned_data["name"]
#             request.session['description_subset'] = form.cleaned_data["description"]
            
#         return HttpResponseRedirect(reverse("machinelearning:ML_build_complex_filter", args=("build_subset",)))
        
# # Function that builds complex filters
# @login_required
# def MLBuildComplexFilter(request, operation):

#     # if filter_string is not initialized, initialize its value to an empty string
#     if (not (request.session.get('filter_string', None))):
        
#         request.session['filter_string'] = ""
#         request.session['filter_string_verbose'] = ""
        
#     # if the user wants to keep building a filter once is already active (filtering active and operation and, or, addop, addparenthesis, unable the filtering
#     if ( (operation == 'and' or operation == "or" or operation == "add_operation" or operation == "add_parenthesis") and (request.session.get('filtering', None)) ):
    
#         del request.session['filtering']
    
#     # manage the operation, adding and changing all the appropiate variables
#     filteringfunctions.manage_operations(request, operation)
    
#     # choose where to redirect
#     if (operation == "build_subset"):
        
#         # clean the rest of filters
#         return HttpResponseRedirect(reverse("machinelearning:ML_reset_filter", args = ("subset_completed",)))
    
#     else:
        
#         return HttpResponseRedirect(reverse("machinelearning:ML_display_filter_data", args=("_id",)))
    

        
# # Function that cleans session variables related to filtering. Useful to clean a previous dataset configuration as well
# @login_required
# def MLResetFilter(request, view_calling):
    
#     # clear filtering variables (of the view)
#     filteringfunctions.clear_filter(request)
    
#     # notify that the session has been modified
#     request.session.modified = True
    
#     # if the call has been made from display_filter data, go to display_filter data view
#     if (view_calling == "display_filter_data"):
        
#         return HttpResponseRedirect(reverse("machinelearning:ML_display_filter_data", args=("_id",)))
    
#     # if the call has been made from dataset configuration view, a new subset is going to be set, so clean the actual subset filters
#     elif (view_calling == "dataset_config"):
            
#         filteringfunctions.clear_filter_subset(request)
            
#         # notify that the session has been modified
#         request.session.modified = True
        
#         return HttpResponseRedirect(reverse("machinelearning:ML_select_variable", args=("dataset_config",)))
    
#     # If the function is called once the subset has been established, go to dataset config (list of dataset) view
#     elif (view_calling == "subset_completed"):
        
#         return HttpResponseRedirect(reverse("machinelearning:ML_dataset_config"))

# # Function that clears the rows of the table
# @login_required
# def MLEraseTable(request):
    
#     model = globals()[request.session['model']]
#     model.objects.all().delete()
    
#     return HttpResponseRedirect(reverse("machinelearning:ML_display_filter_data", args=("_id",)))

# # Detailed view of the fields of each patient
# @login_required
# def MLDetailView(request, id_detail):
    
#     model = globals()[request.session['model']]
    
#     # get the element with the id that matches the one received as a parameter
#     data = model.objects.filter(_id=bson.objectid.ObjectId(id_detail)).values()
    
#     # Get column names
#     fields_ini = model._meta.fields
#     variable_names = []
        
#     for variable in fields_ini:
#         position = stringfunctions.find_nth(str(variable), '.', 2)
#         var_name = str(variable)[position+1:]
#         variable_names.append(var_name)
        
#     # build the title of the view
#     title_content = "Vista detalle del elemento asociado al modelo " + request.session['model'] 

#     return render(request, "ML_detail.html", {'data':data, 'title_content':title_content, 'variable_names':variable_names, 'Id': id_detail})

# # View that contains the index of the EDA - shows all the available variables. Link to univariable/bivariable analysis
# @login_required
# def MLEDAIndexView(request):
    
#     model = globals()[request.session['model']]
    
#     if ("GET" == request.method):
    
#         # Get all the fields of variable of the patient's model
#         data_ini = model._meta.fields
#         variable_pair_list = []

#         for variable in data_ini:
#             position = stringfunctions.find_nth(str(variable), '.', 2)
#             var_string = str(variable)[position+1:]
            
#             # ignore the _id
#             if (var_string != "_id"):
            
#                 # Add it to the pair list that will build the form if it selected in the subset
#                 if (request.session["variables_subset"][var_string]):
#                     variable_pair_list.append((var_string, var_string))

#         form = EdaUnivariableForm()
#         form.select_eda_variable(variable_pair_list)

#         data = variable_pair_list
        
#         # build the title of the view
#         title_content = "Pagina principal de EDA - Modelo " + request.session['model']
                
#         # if there is not an error message to display
#         if (not (request.session.get('error', None))):
#             return render(request, "ML_eda_index.html", {'data': data, 'form':form, 'title_content':title_content })
        
#         else:
#             return render(request, "ML_eda_index.html", {'data': data, 'form':form, 'error_message': request.session['error'], 'error': True, 'title_content': title_content})
    
#     else:
        
#         # get list with the selected variables of the form
#         eda_variables = request.POST.getlist('variable')
        
#         # univariate analysis
#         if (len(eda_variables) == 1):
            
#             # remove the error message if there is one
#             if (request.session.get('error', None)):
#                 del request.session['error']
                
#             return HttpResponseRedirect(reverse('machinelearning:ML_eda', args=[eda_variables[0], '0']))
        
#         elif (len(eda_variables) == 2):
            
#             # remove the error message if there is one
#             if (request.session.get('error', None)):
#                 del request.session['error']
                
#             return HttpResponseRedirect(reverse('machinelearning:ML_eda', args=[eda_variables[0], eda_variables[1]]))
        
#         else:
        
#             request.session['error'] = 'Han de seleccionarse 1 o 2 variables para el EDA'
            
#             return HttpResponseRedirect(reverse("machinelearning:ML_eda_index"))


# # View of the EDA, param are the name of two of the model's fields. If second variable is '0' -> univariate analysis
# @login_required
# def MLEDAView(request, eda_variable, eda_variable2):
    
#     model = globals()[request.session['model']]
    
#     plt.clf()
    
#     if ("GET" == request.method):
    
#         # get first column of data form the database
#         data = model.objects.values_list(eda_variable)
#         data_list = []

#         # Guess if first variable is numerical or not
#         numeric = False
        
#         if (model._meta.get_field(eda_variable).get_internal_type() == "DecimalField"):
#             numeric = True

#         # Build a list with the data and its cirrect type
#         if (numeric):
#             for element in data:
#                 data_list.append(float(element[0]))
#         else:
#             for element in data:
#                 data_list.append(str(element[0]))

#         ########## Univariate analysis ##########

#         # If second variable's string is equal to '0', run univariate analysis 
#         if (eda_variable2 == str(0)):
            
#             univariate_dict = eda.univariate_eda(model, eda_variable, data_list, numeric)
            
#             # build Univariate analysis title
#             if (numeric):
#                 title_content = "Análisis univariable de las variable numérica" + eda_variable + " - Modelo " + request.session["model"]

#             else:
#                 title_content = "Análisis univariable de las variable categórica" + eda_variable + " - Modelo " + request.session["model"]
            
#             return render(request, "ML_univariate_eda.html", {'univariate_dict': univariate_dict, "title_content": title_content})

#        ########## Bivariate analysis ##########
#         else:

#             bivariate_dict = eda.bivariate_eda(model, eda_variable, eda_variable2, data_list, numeric)
    
#             # build Bivariate analysis title
#             if (bivariate_dict["analysis_type"] == "numerical/numerical"):
#                 title_content = "Análisis bivariable de las variables numéricas" + eda_variable + " y " + eda_variable2 + " - Modelo " + request.session["model"]

#             elif (bivariate_dict["analysis_type"] == "numerical/categorical"):
#                 title_content = "Análisis bivariable de las variables numérica y categórica" + eda_variable + " y " + eda_variable2 + " - Modelo " + request.session["model"]

#             elif (bivariate_dict["analysis_type"] == "categorical/categorical"):
#                 title_content = "Análisis bivariable de las variables categóricas" + eda_variable + " y " + eda_variable2 + " - Modelo " + request.session["model"]
            
            
#             return render(request, "ML_bivariate_eda.html", {'bivariate_dict': bivariate_dict, "title_content": title_content})
            
#     else:
            
#         # Get the variable for the bivariate analysis and set the parametes
#         variable = request.POST.getlist('variable')

#         return HttpResponseRedirect(reverse('machinelearning:ML_eda', args=[eda_variable, variable[0]]))

# # View for algorithm selection
# @login_required
# def MLAlgorithmSelectionView(request, problem_string):
    
#     if ("GET" == request.method):
        
#         if (problem_string == "Binary_Classification"):
            
#             # Get the form to select one binary classification algorithm and build the view title
#             form = BinaryClassificationAlgorithmSelectionForm()
#             title_content = "Selección de algoritmos de clasificación binaria - Modelo actual " + request.session["model"]
            
#         elif (problem_string == "Multiclass_Classification"):
            
#             # Get the form to select one multiclass classification algorithm and build the view title
#             form = MulticlassClassificationAlgorithmSelectionForm()
#             title_content = "Selección de algoritmos de clasificación multiclase - Modelo actual " + request.session["model"]
            
#         elif (problem_string == "Regression"):
        
#             # Get the form to select one regression algorithm and build the view title
#             form = RegressionAlgorithmSelectionForm()
#             title_content = "Selección de algoritmos de regresión - Modelo actual " + request.session["model"]
        
#         return render (request, "ML_algorithm_selection.html", locals())
        
#     else:
        
#         # create a form instance and populate it with data from the request:
        
#         if (problem_string == "Binary_Classification"):
            
#             form = BinaryClassificationAlgorithmSelectionFormChar(request.POST)
            
#         elif (problem_string == "Multiclass_Classification"):
            
#             form = MulticlassClassificationAlgorithmSelectionFormChar(request.POST)
            
#         elif (problem_string == "Regression"):
        
#             form = RegressionAlgorithmSelectionFormChar(request.POST)
        
#         # check whether it's valid:
#         if form.is_valid():
            
#             request.session['selected_algorithm'] = form.cleaned_data['algorithm']
            
#             return HttpResponseRedirect(reverse("machinelearning:ML_select_variable", args=("machine_learning",)))
            
        
# # View for selecting the input variables for running the big data algorithm
# @login_required
# def MLSelectVariableView(request, operation):
        
#     model_sf = globals()[request.session['model'] + "SelectionForm"]

#     if ("GET" == request.method):
        
#         # checks if the operation is selecting a variable for classification/regression or to build the subdataset
#         if (operation == "dataset_config"):
        
#             # form with all the variables
#             form = model_sf()
            
#             # Build the title of the view
#             title_content = "Selección de variables de entrada para la configuración del subconjunto de datos - Modelo " + request.session["model"]
            
#         elif (operation == "machine_learning"):
            
#             form = model_sf()
            
#             # hide the fields that were not included in the subdataset configuration
#             for key, value in request.session['variables_subset'].items():
                
#                 if (value == False):
                    
#                     form.fields[key].widget = forms.HiddenInput()
                    
#             # Build the title of the view
#             title_content = "Selección de variables de entrada para el algoritmo - Modelo " + request.session["model"]
        
#         return render(request, "ML_select_variable.html", {'form': form, 'operation': operation, 'title_content':title_content})
    
#     # if not get, then POST 
#     else:
       
#         # create a form instance and populate it with data from the request:
#         form = model_sf(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
            
#             if (operation == "dataset_config"):
            
#                 # For the dataset configuration (select the variables for the subset)
#                 request.session['variables_subset'] = form.cleaned_data
                
#                 # keep configuring the subset in next view (filtering set up)
#                 return HttpResponseRedirect(reverse("machinelearning:ML_display_filter_data", args=("_id",)))
            
#             elif (operation == "machine_learning"):
            
#                 # For the classification algorithms view
#                 request.session['variables_classification'] = form.cleaned_data
            
#                 return HttpResponseRedirect(reverse("machinelearning:ML_select_target"))
        
# # View for selecting the target variable for running the big data algorithm        
# @login_required
# def MLSelectTargetView(request):
        
#     possible_targets = globals()[request.session['model'] + "_CHOICES"]

#     if ("GET" == request.method):
        
#         # get the form and create the choices from possible_targets
#         form = TargetForm()
#         form.create_target(possible_targets)
        
#         # build the title of the view
#         title_content = "Selección de variable objetivo - Modelo " + request.session["model"]
        
#         return render(request, "ML_select_target.html", locals())
    
#     # if not get, then POST 
#     else:
       
#         # create a form instance and populate it with data from the request:
#         form = TargetFormChar(request.POST)
        
#         # check whether it's valid:
#         if form.is_valid():
            
#             # For the classification algorithms view
#             request.session['target'] = form.cleaned_data
            
#             return HttpResponseRedirect(reverse("machinelearning:ML_cluster_set_up"))
        
# # View that manages the cluster set up (distributed execution of algorithms)
# @login_required
# def MLClusterSetUpView(request):

#     if ("GET" == request.method):
        
#         # get the set up form and title
#         form = ClusterSetUpForm()
#         title_content = "Configuración de los parámetros para ejecución distribuida - Modelo " + request.session["model"]
        
#         return render(request, "ML_cluster_set_up.html", locals())
    
#     # if not get, then POST 
#     else:
       
#         # create a form instance and populate it with data from the request:
#         form = ClusterSetUpForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
            
#             # set up all the cluster execution parameters 
#             request.session['distributed'] = form.cleaned_data['distributed']
#             request.session['conexionToSparkMaster'] = form.cleaned_data['conexionToSparkMaster']
#             request.session['numberOfCores'] = form.cleaned_data['numberOfCores']
#             request.session['numberOfCoresPerExecutor'] = form.cleaned_data['numberOfCoresPerExecutor']
#             request.session['executorMemory'] = form.cleaned_data['executorMemory']

#             return HttpResponseRedirect(reverse("machinelearning:ML_algorithm_set_up"))

# # View for algorithm configuration
# @login_required
# def MLAlgorithmSetUpView(request):
    
#     model = globals()[request.session['model']]
    
#     # Build a dictionary with lists of available algorithms
#     algorithms_dict = algorithmsmanagement.get_available_algorithms()
    
#     # If an algorithm has been previously selected
#     if (request.session.get('selected_algorithm', None)):
        
#         # If its a get method,  and show the selected algorithm's form
#         if ("GET" == request.method):
        
#             # Build an empty form for selecting parameters form for the selected algorithm 
#             form_model = algorithmsmanagement.select_algorithm_form(request.session['selected_algorithm'], False)
#             form = form_model()
            
#             # build the title
#             title_content = "Configuración de los parámetros del algoritmo " + request.session['selected_algorithm'] + " para su ejecución con el modelo " + request.session['model']
        
#             return render(request, "ML_algorithm_set_up.html", {'form': form, 'title_content':title_content})
        
#         # If it is a post method build the spark dataframe and run the algorithms
#         else:
            
#             ############# Build pyspark dataframe with the selected variables #############

#             # get shuffled pandas dataframe with selected variables
#             df_vars_dict = algorithmsmanagement.create_df_pandas(request.session['variables_classification'], model, request.session['target']['target'])

#             # create spark session
            
#             # local spark session (using all the cores and a single executor)
#             if (request.session['distributed'] == False):
#                 spark = SparkSession.builder.getOrCreate()
            
#             # distributed spark session, with the configuration from the ClusterSetUp view
#             else:
#                 conf = SparkConf().setMaster(request.session['conexionToSparkMaster']).setAppName("Bdmed")
#                 conf.set("spark.cores.max", str(request.session['numberOfCores']))
#                 conf.set("spark.executor.cores", str(request.session['numberOfCoresPerExecutor']))
#                 conf.set("spark.executor.memory", str(request.session['executorMemory'])+'g')
                
#                 spark = SparkSession.builder.config(conf = conf).appName("Distributed execution of " + request.session['selected_algorithm'] + " algorithm, using model " + request.session['model']).getOrCreate()
            
#             #check deatils of configuration
#             sc = spark.sparkContext
            
#             # create pyspark dataframe from pandas' one        
#             pyspark_df = spark.createDataFrame(df_vars_dict["df"]) 

#             # set algorithm type (classification)
#             is_classification = True
            
#             # apply classification/regression preprocessing to the spark dataframe (get labels and features in the correct format for algorithms)
#             if (request.session['selected_algorithm'] in algorithms_dict["regression_algorithms"]):
#                 preprocessed_df = sparkpreprocessing.spark_df_preprocessing(df_vars_dict["variables_numeric"], df_vars_dict["variables_categoric"],
#                                                                                   request.session['target']['target'], pyspark_df, "Regression")
#                 # set algorithm type (regression)
#                 is_classification = False
                
#             else:
#                 preprocessed_df = sparkpreprocessing.spark_df_preprocessing(df_vars_dict["variables_numeric"], df_vars_dict["variables_categoric"],
#                                                                                   request.session['target']['target'], pyspark_df, "Classification")
            
#             # get schemas and some other relevant information from the preprocessed pyspark df (classification variable mapping, df schema, df 20 first lines, df shape)
#             preprocessed_df_info_dict = algorithmsmanagement.get_df_info(preprocessed_df, request.session['target']['target'], is_classification)
            
#             result_instance_id = algorithmsmanagement.run_algorithm(preprocessed_df, preprocessed_df_info_dict, request.session['selected_algorithm'], request.POST,
#                                                                     request.session['model'], algorithms_dict)
            
#             spark.stop()

#             return HttpResponseRedirect(reverse('machinelearning:ML_result_analysis', args=[request.session['selected_algorithm'], str(result_instance_id)]))
    
#     # algorithm has not been selected
#     else:
            
#         return HttpResponseRedirect(reverse("machinelearning:ML_show_cards", args=["problem-resolution",]))

# # View that shows a list of previous results of algorithms runs
# @login_required
# def MLPreviousResultsView(request):
    
#     # set up all the registered results models
#     models_string = ["BinaryLogisticRegression", "MulticlassLogisticRegression", "BinaryDecisionTree", 'MulticlassDecisionTree', "BinaryRandomForest", "MulticlassRandomForest", "BinaryGBT",
#                      "BinaryNaiveBayes", "MulticlassNaiveBayes", "BinaryLinearSVC", "DecisionTreeRegression", 'RandomForestRegression', 'GBTRegression']
#     models_main_measures = ["aucMean", "f1Mean", "aucMean", "f1Mean", "aucMean", "f1Mean", "aucMean", "aucMean", "f1Mean", "aucMean", "rmseMean", "rmseMean", "rmseMean"]
    
#     # set up return lists
#     populated_models = []
#     model_instances = []
        
#     for model_string, measure in zip(models_string, models_main_measures):
        
#         model_instances_local = []
        
#         # get the model variable
#         model = globals()[model_string + "Result"]
        
#         # get the instances of results (order by date, newest first)
#         results = model.objects.order_by('-dateOfCreation').values_list("id", "dateOfCreation", measure)
        
#         # if there is any instance of the model result, append it to the return list
#         if (len(results) > 0):
            
#             # make a list of Id, Date of creation and Measure for each result
#             for elem in results:
#                 IDM_list = []
#                 IDM_list.append(str(elem[0])) # Id
#                 IDM_list.append(str(elem[1])[0:19]) # DateofCreation
#                 IDM_list.append(str(elem[2])) # Measure
#                 model_instances_local.append(IDM_list)
            
#             # get the final model and instances list
#             populated_models.append(model_string)
#             model_instances.append(model_instances_local)
            
#     # build the title of the view
#     title_content = "Resultados de ejecuciones previos"
            
#     return render (request, "ML_previous_results.html", {'populated_models_instances': zip(populated_models,model_instances,models_main_measures), "title_content": title_content})

# # View that shows the results of an execution
# @login_required
# def MLResultAnalysisView(request, algorithm_string, id_instance):
    
#     model = globals()[algorithm_string + "Result"]
    
#     # Build the list of available algorithms
#     algorithms_dict = algorithmsmanagement.get_available_algorithms()
    
#     # get the instance of the model
# #     ri = model.objects.filter(_id=bson.objectid.ObjectId(id_instance)).values()[0]
#     ri = model.objects.filter(id=int(id_instance)).values()[0]
    
#     # build the title of the view
#     title_content = "Resultados para el algoritmo " + algorithm_string + " con el modelo " + ri["model"]
    
#     if (algorithm_string in algorithms_dict["logistic_algorithms"]):
    
#         return render(request, "ML_result_analysis.html", {'selected_algorithm':algorithm_string, 'ri': ri, 'title_content': title_content})
    
#     elif (algorithm_string in algorithms_dict["binary_classification_algorithms"]):
    
#         return render(request, 'ML_result_analysis.html', {'type':'Binary', 'selected_algorithm':algorithm_string, 'ri': ri, 'title_content': title_content})
    
#     elif (algorithm_string in algorithms_dict["multiclass_classification_algorithms"]):
        
#         return render(request, 'ML_result_analysis.html', {'type':'Multiclass', 'selected_algorithm':algorithm_string, 'ri': ri, 'title_content': title_content})
    
#     elif (algorithm_string in algorithms_dict["regression_algorithms"]):
        
#         return render(request, 'ML_result_analysis.html', {'type':'Regression', 'selected_algorithm':algorithm_string, 'ri': ri, 'title_content': title_content})