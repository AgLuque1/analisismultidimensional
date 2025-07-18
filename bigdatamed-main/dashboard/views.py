
from scipy.fftpack import ss_diff
from dashboard.forms import NewExperimentForm, ProfileForm
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse

import json
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
import requests
from django.contrib.auth.decorators import login_required
from .models import Category, Experiment, User, ProblemSelection
from .models import User
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

# Library for managing all types of algorithms (creation of images, preprocessing, etc.)
from .tools import algorithmsmanagement 
# Library with the code of all clustering algorithms
from .tools import clustering 

# Create your views here.
@login_required
def home(request):    
            
    categories = Category.objects.filter()

    # set title of the view
    title_content = "Dashboard"

    # set active button of the sidebar
    sidebar_active = None
        
    return render(request,"home.html", locals())

@login_required
def profile_user(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST or  None, request.FILES or None)
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            user.first_name = request.POST.get('first_name')
            user.last_name  = request.POST.get('last_name')
            user.email      = request.POST.get('email')
            
            user.profile.address    = request.POST.get('address')
            user.profile.education  = request.POST.get('education')
            user.profile.skill      = request.POST.get('skill')
            user.profile.bio        = request.POST.get('bio')
            try:
                user.profile.image      = request.FILES['image']
            except:
                user.profile.image = user.profile.image

            user.profile.save()
            user.save()
            return redirect('dashboard:profile_user')
    else:
        user_object = User.objects.get(pk=request.user.id)
        data = {
            'first_name':user_object.first_name,
            'last_name': user_object.last_name,
            'email':user_object.email,
            'address':user_object.profile.address,
            'education':user_object.profile.education,
            'skill':user_object.profile.skill,
            'bio':user_object.profile.bio
        }
        profileForm = ProfileForm(data)
    
    return render(request,"profile.html",locals())

# view that shows the experimentation workflow and starts a new experimentation
@login_required
def createExperimentationView(request):

    # GET - render a template with an empty experimentation form and previous experiments   
    if request.method == 'GET':

        # set title of the view
        title_content =  "Crear Experimentación" 

        # set active button of the sidebar
        sidebar_active = "experimentation"

        # Load form NewExperiment => NewExperiment is in file form.py

        # if the current user is an admin
        all_bbdd = requests.get(settings.URL_CONFIG_API_REST + 'getAdminDBVerbose')
       
        # create the correct structure for NewExperimentForm choices
        all_bbdd = json.loads(all_bbdd.text)
        listof_dict_aux = []
        for elem in all_bbdd:
            dict_aux = dict()
            dict_aux[elem["dataset"]] = elem["verbose"]
            listof_dict_aux.append(dict_aux)
        all_bbdd = listof_dict_aux
        all_bbdd_dictionary = {k: v for element in all_bbdd for k, v in element.items()}

        # store the dictionary in a session variable
        request.session["all_bbdd_dictionary"] = all_bbdd_dictionary

        # create the empty experiment Form
        formNewExperiment = NewExperimentForm(all_bbdd=all_bbdd)

        # Get all previous experiments from user - Pagination is now managed by DataTable's system
        all_experiments = Experiment.objects.filter(user=request.user.pk).order_by('-date_create')

        # Change the name of the experiment to the verbose version
        dict_exp_verbose = {}
        for exp in all_experiments:

            # change name to verbose
            exp.name_bbdd = all_bbdd_dictionary[exp.name_bbdd]

        return render(request, "create_experimentation.html",locals())

    # POST REQUEST - create a new experiment object, store it in the DB and set to request session variable
    else:

        form = NewExperimentForm(request.POST or  None, request.FILES or None,
        all_bbdd=[{request.POST["name_bbdd"]:request.POST["name_bbdd"]}])
        
        if form.is_valid():

            name_exp    = request.POST['name']
            
            # Filter with the option of it doesn't insert date_end or date_init
            if not request.POST['date_end']:
                date_end = None
            else:
                date_end    = datetime.strptime(request.POST['date_end'],'%d/%m/%Y').date()
            
            if not request.POST['date_init']:
                date_init = None
            else:
                date_init   = datetime.strptime(request.POST['date_init'],'%d/%m/%Y').date()

            filter_apply = None
            user_object = User.objects.get(pk=request.user.id)
            
            # Get key value bbdd request.POST['select_bbdd']
            select_bbdd = request.POST['name_bbdd']

            # Get meta information of the database that has been selected
            response_meta    =  requests.get(settings.URL_CONFIG_API_REST +select_bbdd+'/meta')
            meta_description = json.loads(response_meta.text)
   
            # Create object for the new experiment 
            new_exp = Experiment.objects.create(user=user_object, name=name_exp,name_bbdd=select_bbdd,
            date_init=date_init, date_end=date_end, filter_apply=filter_apply )

            # Store object in models
            new_exp.save()  

            # Get date create from object new_exp
            field_object = Experiment._meta.get_field('date_create')
            date_create_exp = getattr(new_exp,field_object.attname)

            # Get the categories of the variables (we get the info from meta_description)

            # get all categories
            categories = []
            for elem in meta_description:
                categories.append(elem["Category"])

            # remove duplicates from categories list
            categories = list(dict.fromkeys(categories))
            
            # Update session variable
            request.session['id_exp'] = new_exp.pk
            request.session['date_create_exp'] = str(date_create_exp)
            request.session['name_exp']        = name_exp
            request.session['select_bbdd']     = select_bbdd
            request.session['select_bbdd_verbose'] = request.session["all_bbdd_dictionary"][select_bbdd] # verbose name
            request.session['date_init']       = str(date_init)
            request.session['date_end']        = str(date_end)
            request.session['filter_apply']    = None
            request.session['meta_description'] = meta_description
            request.session['categories']      = categories

            return HttpResponseRedirect(reverse("dashboard:config_dataset"))

# configDatasetView => View shows the meta description of the selected dataset and allows the user to visualize the datasets and select the variables
@login_required
def configDatasetView(request):

    # set title of the view
    title_content = "Selección e información de campos del DataSet"

    # set active button of the sidebar
    sidebar_active = "configDataset"

    data = request.session['meta_description']

    return render(request, "config-dataset.html", locals())

# load_experiment => View load experiment select in the table
@login_required
def load_experiment(request, operation):
   
    # Store all relevant values into the session variable. Values taken from the selected row of the table of previous experiments
    request.session['id_exp']           = request.POST['id_exp']
    request.session['date_create_exp']  = request.POST['date_create_exp']
    request.session['name_exp']         = request.POST['name_exp']
    request.session['date_init']        = request.POST['date_init']
    request.session['date_end']         = request.POST['date_end']
    request.session['select_bbdd_verbose'] = request.POST['select_bbdd']

    # verbose name to code name
    request.session['select_bbdd'] = dict((v, k) for k, v in request.session["all_bbdd_dictionary"].items())[request.POST['select_bbdd']]
    
    # if there is not a filter applied, set it to None
    if (request.POST['filter_apply'] != "Ninguno seleccionado. Es necesario seleccionar variables."):
        request.session['filter_apply']     = Experiment.objects.get(pk=request.POST['id_exp']).filter_apply
    else:
        request.session['filter_apply']     = None

    # Get meta information of the database that has been selected (code name)
    response_meta    =  requests.get(settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + '/meta')

    meta_description = json.loads(response_meta.text)
    
    request.session['meta_description'] = meta_description

    # Get the categories of the variables (we get the info from meta_description)

    # get all categories
    categories = []
    for elem in meta_description:
        categories.append(elem["Category"])

    # remove duplicates from categories list
    categories = list(dict.fromkeys(categories))

    request.session['categories'] = categories

    # if we are creating a new experiment, the experiment has not got any selected variables/filter or the selected operation is edit
    # go to config dataset view
    if (request.session['filter_apply'] == None or operation == "Edit"):

        return HttpResponseRedirect(reverse("dashboard:config_dataset"))

    # send a post request to the manage filter function with the information stored in filter_apply field of the database
    else:

        # create the input with the info of the loaded filter
        filter_apply_info = eval(request.session['filter_apply'])

        post_data = {'filter-categories': filter_apply_info['filter_categories_dict'],
         'filter-intervals': filter_apply_info['filter_intervals_dict'], 
         'selected-variables': filter_apply_info['selected_variables']}

        response = requests.post("http://" + request.get_host() + '/manage-filter', data={"json_string": json.dumps(post_data), 
        "select_bbdd":request.session["select_bbdd"]})

        # store the loaded dataset in a session variable
        request.session["filtered_dataframe"] = response.json()['filtered_data']

        return HttpResponseRedirect(reverse("dashboard:problem_selection"))

# remove_exp_table => View remove object experiment to click in icon trash inside table
@login_required
def remove_exp_table(request, id_exp):

    object_experiment = Experiment.objects.get(pk=id_exp)

    # if it is the current experiment, delete session variables
    if ('id_exp' in request.session and id_exp == request.session['id_exp']):
        del request.session['id_exp']
        del request.session['date_create_exp']
        del request.session['name_exp']
        del request.session['select_bbdd']
        del request.session['select_bbdd_verbose']
        del request.session['date_init']
        del request.session['date_end']
        del request.session['filter_apply']
        del request.session['meta_description']
        del request.session['categories']

    object_experiment.delete()
    return JsonResponse({'isConfirm':True})

# plot_variable => View that queries a database and gives the information to plot a numerical/categorical variable
@login_required
def plot_variable(request):

    # store in a variable the selected variable (and its type) that were stored as a string in the POST request info
    var_name = request.POST.get("new_variable")
    var_type = request.POST.get("var_type")

    # If the type of variable is categorical, we need to count the number of elements of each category of the variable
    if (var_type == "Categorical"):

        # Database query - get all data of the selected Categorical variable and make it json (doughnut diagram)
        response_data = requests.get(settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + '/' + var_name + "/countCategories")
        response_data = json.loads(response_data.text)

        # get labels (name of the categories) and data (number of appareances of each category in the registers of the variable)
        # from the response data of the API
        labels = []
        data = []
        for dictionary in response_data:
            labels.append(dictionary['_id'])
            data.append(dictionary['count'])

        # Build the structure that the function is going to return
        result_dict = dict()
        result_dict['var_name'] = var_name
        result_dict['var_type'] = var_type
        result_dict['data'] = data
        result_dict['labels'] = labels

    elif (var_type == "Numerical"):

        # Database query - get all data of the selected Numerical variable and make it json (histogram)
        response_data = requests.get(settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + '/' + var_name + "/histogram")

        # Build the structure that the function is going to return
        result_dict = json.loads(response_data.text)
        result_dict['var_name'] = var_name
        result_dict['var_type'] = var_type

    return JsonResponse({'success': True, "data_dict": result_dict}, status=200)

@login_required
def filter_dataset(request):
    """ View donde se almacena los valores por defecto que muestra los filtros por filas   

    Args:
        request (_type_): _description_

    Returns:
        _render_: _template html_
    """
  
    if request.POST:
        categories = request.POST['category-selected'].split(",")
        variables = request.POST['variable-selected'].split(",")

        """
            Diccionario lista de columnas
        """
        dictionary_list_var = []
        for variable in variables:
            dictionary_variable = {}
            key   = variable.replace("{ ","").replace(" }","").split("|")[0] 
            value = variable.replace("{ ","").replace(" }","").split("|")[1]
            dictionary_variable[key]= value
            dictionary_list_var.append(dictionary_variable)

        """
            Diccionario valores de las columnas
        """        
        dictionary_navs = []
        for cat in categories:
            dictionary_cat = {}
            dictionary_cat[cat] = []
            for elem in dictionary_list_var:
                for k,v in elem.items():
                    if cat == v:
                        dictionary_cat[cat].append(k.replace(" ",""))
                        
                
            dictionary_navs.append(dictionary_cat)
    
        request.session['dictionary_navs'] = dictionary_navs

        # category that is going to be active when the view is rendered
        request.session['first_category'] = list(dictionary_list_var[0].values())[0]

        return HttpResponseRedirect(reverse("dashboard:filter_dataset"))

    else:
        
        # set title of the view
        title_content = "Selección de Filtros"

        # set active button of the sidebar
        sidebar_active = "configDataset"

        return render(request, "filter-dataset.html", locals()) 

# Function that handles de ajax request from the filter view and calls the API for the categories/intervals information
@login_required
def get_filter_variable_dictionary(request):

    dictionary = {}
    
    dictionary[request.POST.get("var_name")]={}
    
    response = requests.get(settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + "/" + request.POST.get("var_name"))            
    result_dict = json.loads(response.text)    

    print(result_dict)
    
    dictionary[request.POST.get("var_name")] = {
                            'category':        result_dict['Category'],
                            'description':      result_dict['Description'],
                            'var_type':         result_dict['VarType'],
                            'values':           result_dict['values']
                            }
    
    request.session['dictionary'] = dictionary

    return JsonResponse({'success': True, 'dictionary': dictionary}, status=200)

# function that manages the information from the filter view
@csrf_exempt
def manage_filter(request):

    # if the request does not have information about the selected variables, pick them from the session variable. Post Request from loadexperiment
    if ('json_string' in request.POST.keys()):
        
        # in here, the user is loading a previous experimentation. Data come from a string

        # process the string and get the information in python format
        post_dict = eval(request.POST['json_string'].replace(": true", ": True").replace(": false", ": False"))
        filter_dict = {"filter_categories_dict":post_dict['filter-categories'] , "filter_intervals_dict":post_dict['filter-intervals'],
        "selected_variables": post_dict['selected-variables']}

        # call the API and store its response
        response = requests.post(settings.URL_CONFIG_API_REST + request.POST['select_bbdd'] + "/filteredData", json = filter_dict)

        return JsonResponse({'success': True, 'filtered_data': response.json()}, status=200)

    # if the user is creating or editing a experiment, change its filter_apply value here and save/update the experiment in the database
    else:

        # get the parameters that will be send to the API (filters and variables)
        filter_categories_dict = json.loads(request.POST['filter-categories'])
        filter_intervals_dict = json.loads(request.POST['filter-intervals'])

        selected_variables = []
        for di in request.session['dictionary_navs']:
            for variables in di.values():
                for variable in variables:
                    selected_variables.append(variable)

        # store all the parameters in a dictionary
        filter_dict = {"filter_categories_dict":filter_categories_dict , "filter_intervals_dict":filter_intervals_dict,
        "selected_variables": selected_variables}

        # call the API and store its response
        response = requests.post(settings.URL_CONFIG_API_REST + request.session['select_bbdd'] + "/filteredData", json = filter_dict)

        # store it in a session variable
        request.session["filtered_dataframe"] = response.json()

        exp = Experiment.objects.get(pk=request.session["id_exp"])
        exp.filter_apply = filter_dict
        exp.save()

        # Actualize the session variables with the new values of the experiment
        request.session['id_exp'] = exp.pk
        request.session['date_create_exp'] = str(exp.date_create)
        request.session['name_exp']        = exp.name
        request.session['select_bbdd']     = exp.name_bbdd
        request.session['select_bbdd_verbose'] = request.session["all_bbdd_dictionary"][exp.name_bbdd] # verbose name
        request.session['date_init']       = str(exp.date_init)
        request.session['date_end']        = str(exp.date_end)
        request.session['filter_apply']    = exp.filter_apply

        return HttpResponseRedirect(reverse("dashboard:problem_selection"))

# function that manages the view related to the problem selection
@login_required
def problemSelectionView(request):

    # set title of the view
    title_content = "Selección de problema a resolver"

    # set active button of the sidebar
    sidebar_active = "knowledgeExtraction"

    problems = ProblemSelection.objects.all()

    return render(request, "problem-selection.html", locals()) 

# function that manages the view related to the algorithm selection and set up. Also the results
@login_required
def algorithmSelectionSetupView(request, problem_string):

    # set up the available algorithms depending on the selected problem
    available_algorithms = algorithmsmanagement.getAvailableAlgorithms(problem_string)

    # set title of the view
    title_content = "Selección y configuración de parámetros del algoritmo - " + problem_string

    # set active button of the sidebar
    sidebar_active = "knowledgeExtraction"

    return render(request, "algorithm-selection-setup.html", locals()) 

# function that handles the ajax post request and sends to the view the information about the algorithm parameters linked to the selected problem
@login_required
def get_info_parameters_algorithm(request):

    problem_string = request.POST['problem_string']

    # get the algorithm parameters of all the algorithms associated to the selected problem
    algorithm_parameters = algorithmsmanagement.getAlgorithmParameters(problem_string)

    return JsonResponse({'success': True, 'algorithm_parameters': algorithm_parameters}, status=200)

# function that handles the ajax post request and sends to the view the information about the parameters of a distributed execution
@login_required
def get_distributed_parameters(request):

    # get the dictionary with the parameters calling the algorithmsmanagement module
    distributed_parameters = algorithmsmanagement.getDistributedParameters()

    return JsonResponse({'success': True, 'distributed_parameters': distributed_parameters}, status=200)

# function that handles the ajax post request and sends to the view the results of the elbow method with the selected dataset
@login_required
def run_elbow_method(request):

    # call to the function that provides the image of the cost of each cluster 
    image = clustering.elbowMethod(request.session["filtered_dataframe"], request.session['meta_description'])
    import ipdb; ipdb.set_trace();
    return JsonResponse({'success': True, 'image': image}, status=200)

# function that handles the ajax post request and sends to the view the results of the algorithm run
@login_required
def run_algorithm(request):

    if (request.POST["algorithm_name"] == "Kprototypes"):
        dict_results = clustering.runKPrototypes(request.session["filtered_dataframe"], request.session['meta_description'],
        request.POST['algorithm_parameters'], request.POST['null_parameters'])

    elif (request.POST["algorithm_name"] == "KmeansDistributed"):
        dict_results = clustering.runKmeansDistributed(request.session["filtered_dataframe"], request.session['meta_description'], 
        request.POST['algorithm_parameters'], request.POST['null_parameters'])

    return JsonResponse(dict_results, status=200)