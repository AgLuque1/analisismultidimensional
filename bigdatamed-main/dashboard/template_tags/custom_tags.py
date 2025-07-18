from django.template.defaulttags import register

@register.filter
def get_item_description(dictionary, key):
    return dictionary[key]['description']

@register.filter
def get_item_var_type(dictionary, key):
    return dictionary[key]['var_type']

@register.filter
def get_item_values(dictionary, key):
    return dictionary[key]['values']

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# tag that transforms the filter of a experimentation to verbose
@register.filter
def get_info_filter(dictionary):

    if (dictionary != None):

            dict_filter = eval(str(dictionary))

            string_selected_variables = "Variables Seleccionadas: <b>" + "</b>, <b>".join(dict_filter['selected_variables']) + "</b>"
            string_cat_variables = ""
            string_num_variables = ""

            if (len (dict_filter['filter_categories_dict']) > 0):
                string_cat_variables += "<br/><br/>Variables <b>categóricas</b> y sus categorías seleccionadas:"
                for cat_variable in dict_filter['filter_categories_dict'].keys():
                    list_aux = [str(k) for k, v in dict_filter['filter_categories_dict'][cat_variable].items() if v]
                    string_cat_variables += "<br/><b>" + cat_variable + "</b>: " + ", ".join(list_aux)

            if (len (dict_filter['filter_intervals_dict']) > 0):
                string_num_variables += "<br/><br/>Variables <b>numéricas</b> y sus intervalos:"
                for num_variable in dict_filter['filter_intervals_dict'].keys():
                    list_aux = [str(v) for v in dict_filter['filter_intervals_dict'][num_variable].values()]
                    string_num_variables += "<br/><b>" + num_variable + "</b>: " + ", ".join(list_aux)

            return string_selected_variables + string_cat_variables + string_num_variables
    else:

        return "Aún no hay filtros activos"