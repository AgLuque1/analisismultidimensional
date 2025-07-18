from . import stringfunctions # for getting images and string manipulation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # for pagination
from ..models import * # import all models

# Python useful libraries
import pandas as pd

"""
Function that clears the session variables that manage the filter made in the view

Parameters:

request: info of the request of the view that calls this function (MLResetFilter)

Return:
"""
def clear_filter(request):
    
    # clear filtering variables (of the view)
    if ((request.session.get('variable_filter', None))):
        del request.session['variable_filter']
        
    if ((request.session.get('operator_filter', None))):
        del request.session['operator_filter']
        
    if ((request.session.get('value_filter', None))):
        del request.session['value_filter']
        
    if ((request.session.get('filter_string', None))):
        del request.session['filter_string']
        
    if ((request.session.get('filter_string_verbose', None))):
        del request.session['filter_string_verbose']
        
    if ((request.session.get('filtering', None))):
        del request.session['filtering']

"""
Function that clears the session variables that manage the active subset

Parameters:

request: info of the request of the view that calls this function (MLResetFilter)

Return:
"""
def clear_filter_subset(request):
    
    if ((request.session.get('subset_built', None))):
        del request.session['subset_built']
            
    if ((request.session.get('variables_subset', None))):
        del request.session['variables_subset']

    if ((request.session.get('filter_string_subset', None))):
        del request.session['filter_string_subset']

    if ((request.session.get('filter_string_subset_verbose', None))):
        del request.session['filter_string_subset_verbose']
        
    if ((request.session.get('name_subset', None))):
        del request.session['name_subset']
        
    if ((request.session.get('description_subset', None))):
        del request.session['description_subset']

"""
Function that manages the filtering operation and creates the Q filter for django queries. 

Parameters:
request: info of the request of the view that calls this function (MLResetFilter)
operation: Operation that is going to be computed in the filtering process. operations can be
 - 'and'
 - 'or'
 - 'add_operation'
 - 'add_parenthesis'
 - 'run_filter'
 - 'build_subset'

Return:
"""
def manage_operations(request, operation):
    
    # if the operation received is an and, add the & and 'AND' symbols to the strings
    if (operation == 'and'):
        
        request.session['filter_string'] += " & "
        request.session['filter_string_verbose'] += " AND "
    
    # if the operation received is an or, add the | and 'OR' symbols to the strings
    elif (operation == 'or'):
        
        request.session['filter_string'] += " | "
        request.session['filter_string_verbose'] += " OR "
    
    # if the operation received is a filter operation (variable-djangoOperator-value), add the Q filter and a verbose version to the strings
    elif (operation == 'add_operation'):
        
        request.session['filter_string'] += "Q(" + request.session['variable_filter'] + '__' + request.session['operator_filter'] + "=" + str(request.session['value_filter']) + ")"
        request.session['filter_string_verbose'] +=  "(" + request.session['variable_filter'] + ' ' + request.session['operator_filter'] + " " + str(request.session['value_filter']) + ")"
    
    # nesting operation, add parenthesis that wrap up all the content of the filter
    elif (operation == 'add_parenthesis'):
        
        request.session['filter_string'] = "(" + request.session['filter_string'] + ")"
        request.session['filter_string_verbose'] = "(" + request.session['filter_string_verbose'] + ")"
    
    # if the operation is running a filter in display_filter_data view, turn on the filtering flag
    elif (operation == 'run_filter'):
        
        request.session['filtering'] = True
    
    # if the operation is building a new subset, turn on the build_subset flag, store the filtering  and clean all the filters
    elif (operation == 'build_subset'):
        
        request.session['subset_built'] = True
        request.session['filter_string_subset'] = request.session['filter_string']
        request.session['filter_string_subset_verbose'] = request.session['filter_string_verbose']
        
        # create the dictionary that will create the subset model
        dict_subset = {}
        dict_subset["qFilter"] = request.session['filter_string_subset']
        dict_subset["verboseFilter"] = request.session['filter_string_subset_verbose']
        dict_subset["selectedVariables"] = request.session['variables_subset']
        dict_subset["relatedModel"] = request.session['model']
        dict_subset["name"] = request.session['name_subset']
        dict_subset["description"] = request.session['description_subset']
        
        # create subset model
        SubsetConfig(**dict_subset).save()

"""
This function builds a dicionary with the names of the selected variables in filtering process. It drops the variables that have not been selected. 

Parameters:
request: info of the request of the view that calls this function (MLResetFilter)
model: Active model or dataset of the database

Return: variables_dict: Dictionary with two fields:
 - variable_names: list with the names (strings) of the selected variables for building the subset
 - variable_pairs_form: List with pairs of these variables. Used for the creation of the dynamic choices in filtering form.
"""
def get_dataset_variables(request, model):
    
    variables_dict = {}
    
    # Get selected columns, based on the variables that were selected in view MLSelectVariableView
    fields_ini = model._meta.fields
    variable_names = []
    variable_pairs_form = []

    for variable in fields_ini:
        position = stringfunctions.find_nth(str(variable), '.', 2)
        var_name = str(variable)[position+1:]

        # Ignore _id field
        if (var_name != "_id"):

            # if the variable takes part of the selected subataset
            if (request.session['variables_subset'][var_name] == True):

                # insert the variable name in var_name, used to select the variables to display
                variable_names.append(var_name)

                # insert variables in pairs, used to build the choices of the filtering form
                variable_pairs_form.append((var_name, var_name))

    # Add _id field
    variables_dict["variable_names"] = ["_id"] + variable_names
    variables_dict["variable_pairs_form"] = [("_id", "_id")] + variable_pairs_form
    
    return variables_dict

"""
This function runs the pagination of the displary data and filtering view (MLDisplayFilterDataView)

Parameters:
request: info of the request of the view that calls this function (MLResetFilter)
data_filtered: queryset with filters related to the creation of the subset applied to the original dataset.
order_variable: final data will be ordered by this variable (string)

Return: pagination_dict: Dictionary with four fields:
 - page: number of current page from request
 - current_order: curront order of the order variable it can be '+', '-' or None
 - dictionary_list: sorted data in list format
 - data: data in django pagination format
"""
def run_pagination(request, data_filtered, order_variable):
    
    # dictionary that will contain the return value of the function
    pagination_dict = {}
    
    # set up paginator
    paginator = Paginator(data_filtered, 20)
    pagination_dict["page"] = request.GET.get('page')

    try:
        data = paginator.page(pagination_dict["page"])
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    # sort values by variable if needed and keep the current order
    dictionary_list = [] 
    if ( len(data) > 0 ):

        # create a dataframe and sort it

        # build the df with the columns
        list_aux = pd.DataFrame(data[0].items()).transpose().values.tolist()
        cols = list_aux[0]
        df = pd.DataFrame(columns=cols)

        # insert all the rows (20 from pagination)
        for elem in data:
            list_aux = pd.DataFrame(elem.items()).transpose().values.tolist()
            df.loc[len(df)] = list_aux[1]

        # order the df descending/ascending
        if (order_variable[0] == "-"):
            pagination_dict["current_order"] = "-"
            df.sort_values(by=order_variable[1:], inplace=True, ascending=False, ignore_index = True)
        else:
            pagination_dict["current_order"] = "+"
            df.sort_values(by=order_variable, inplace=True, ignore_index = True)

        # Build the dictionary list
        for i in range(len(df)):
            df_aux = pd.DataFrame(columns=cols)
            df_aux.loc[0] = df.loc[i]
            dictionary_list.append(df_aux.to_dict('records'))

    else:
        pagination_dict["current_order"] = 'none'
        
    # add dictionary list (sorted 20 first values) and data (data of the page) to the return dictionary
    pagination_dict["dictionary_list"] = dictionary_list
    pagination_dict["data"] = data
        
    return pagination_dict

"""
This function converts the operator of the filter form in the one that Django uses in filtering.

Parameters:
form: VariableFilterFormChar, with the string that is going to be changes in field ".cleaned_data['operator']"

Return:
"""
def translate_operator(form):
    
    if (form.cleaned_data["operator"] == "Igual que"):
        form.cleaned_data["operator"] = "exact"
        
    elif (form.cleaned_data["operator"] == "Igual que (no sensible a mayus)"):
        form.cleaned_data["operator"] = "iexact"
        
    elif (form.cleaned_data["operator"] == "Contiene"):
        form.cleaned_data["operator"] = "contains"
        
    elif (form.cleaned_data["operator"] == "Contiene (no sensible a mayus)"):
        form.cleaned_data["operator"] = "icontains"
        
    elif (form.cleaned_data["operator"] == "Mayor que"):
        form.cleaned_data["operator"] = "gt"
        
    elif (form.cleaned_data["operator"] == "Mayor o igual que"):
        form.cleaned_data["operator"] = "gte"
        
    elif (form.cleaned_data["operator"] == "Menor que"):
        form.cleaned_data["operator"] = "lt"
        
    elif (form.cleaned_data["operator"] == "Menor o igual que"):
        form.cleaned_data["operator"] = "lte"
        
    elif (form.cleaned_data["operator"] == "Empieza por"):
        form.cleaned_data["operator"] = "startswith"
        
    elif (form.cleaned_data["operator"] == "Empieza por (no sensible a mayus)"):
        form.cleaned_data["operator"] = "istartswith"
        
    elif (form.cleaned_data["operator"] == "Termina por"):
        form.cleaned_data["operator"] = "endswith"
        
    elif (form.cleaned_data["operator"] == "Termina por (no sensible a mayus)"):
        form.cleaned_data["operator"] = "iendswith"
        
    elif (form.cleaned_data["operator"] == "Expresión regular"):
        form.cleaned_data["operator"] = "regex"
        
    elif (form.cleaned_data["operator"] == "Expresión regular (no sensible a mayus)"):
        form.cleaned_data["operator"] = "iregex"