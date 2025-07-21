// *** Initial value of global variables ***
selectedCategoriesDictionary = {};
selectedIntervalsDictionary = {};

// *** csrftoken initial configuration ***

// set up the csrftoken using jQuery, for AJAX POST. Django forces to do this if we want to use AJAX.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// Get the token and store it in a const variable
const csrftoken = getCookie('csrftoken');

// *** Functions for initial configuration of the view ***

/**
 * document ready function, runs functions once the web (DOM) is fully loaded
 */
 $(document).ready(function() {

    // get the name of the recent selected variable
    varName = $(".first-column")[0].id;

    // generate the initial Table of categories/Numeric intervals, bound to the variable selected by default
    generatePopulateTableCategoriesNumericalIntervals(varName);

});

/**
 * Function/Listener that calls the API to get the information of the selected variable when a nav-link element is clicked
 */
 $(".nav-link-category").on('click', function(){

    // get the name of the recent selected variable
    varName = this.id.substr(0, this.id.length-4);

    // deactivate the previous active nav
    $(".nav-link-category.active").removeClass("active")

    // generate the Table of categories/Numeric intervals, bound to the variable of the nav-link just selected
    generatePopulateTableCategoriesNumericalIntervals(varName);

});

/**
 * Function/Listener that links the current module (filtering) with the following one (problem solving selection)
 */
 $("#next_module").on('click', function(){

    $("#request-filter-categories")[0].value = JSON.stringify(selectedCategoriesDictionary);
    $("#request-filter-intervals")[0].value = JSON.stringify(selectedIntervalsDictionary);

});

/// *** Main function that handles the generation of Table of categories and Numerical intervals ***

/**
 * Function that makes the ajax call to generate and populate the table with Categories/Numerical intervals
 */
 function generatePopulateTableCategoriesNumericalIntervals(varName){

    // Remove the content of the filter containers
    for (i=0; i<$(".filter-container").length;i++ ){
        $(".filter-container")[i].innerHTML = "";
    }

    // Add a loading text while the post request is sent and managed
    $("#"+varName)[0].innerHTML="Generando tabla o intervalo..."

    // address where the POST request is going to be sent (Django View)
    address = window.location.origin + '/ajax/get_filter_variable_dictionary';

    // Ajax POST request
    $.ajax({
        url: address,
        cache:'false',
        dataType: 'json',
        type:"POST",
        data: {"var_name": varName},
        headers:{
            "X-CSRFToken": csrftoken
        },
        async: true,
        success: function(data){

            // if the function successes, there will be a field called success that have been set to true in the Django view
            if (data.success){

                if (data.dictionary[varName]['var_type'] == "Categorical"){
                    generateCategoricalFilter(varName, data);
                }
                else{
                    generateNumericalFilter(varName, data);
                }
                
            }
            else{
                alert("error: data didn't success");
            }
            
        },
        error: function(){
            alert('error; ');
        }
    });

}

/// *** Functions for managing Table of categories ***

/**
 * Function that generates a table with the available categories for the selected variable
 */
 function generateCategoricalFilter(varName, data){

    // create the new html data with the info coming from the ajax async request and set it into the correct section
    generateTableCategoriesHtml(varName, data);

    // refresh the table so it renders properly
    initializeRefreshTableCategories();

    // set up the "select all categories" button
    $("#select_deselect_all").on('click', selectAllListener);

    // get all categories of the variable
    categories = $("#table_categories").DataTable().columns(0).data()[0];

    // if the variable is selected for the first time, actualize the global variable with a dictionary
    if (!(varName in selectedCategoriesDictionary)){
        selectedCategoriesDictionary[varName] = {};

        // initialize all the categories of the variable to false
        for (i=0; i<categories.length; i++){
            selectedCategoriesDictionary[varName][categories[i]] = false;
        }
        
        refreshFiltersInformation();

    }

    // if not, get the previously selected categories and actualize the table
    else {

        // get the previous selected categories of the table from the global variable
        selected_rows = [];
        for (i=0; i<categories.length; i++){
            if (selectedCategoriesDictionary[varName][categories[i]] == true){
                selected_rows.push(i);
            }
        }

        // select all rows at once
        $("#table_categories").DataTable().rows( selected_rows ).select();
    }

}

/**
 * Function that generates the html code of the Table of Categories
 */
 function generateTableCategoriesHtml(varName, data){

    // create the new html data with the info coming from the ajax async request
    content_html = 
    "<table id='table_categories' class='table table-striped table-bordered table-sm' cellspacing='10' width='100%'>"
    + "<thead>"
    + "<tr>"
    + "<th>Categoría</th>"
    + "<th>"
    + "<div class='form-check form-check-custom'>"
    + "<input id='select_deselect_all' class='form-check-input' type='checkbox' value=''>"
    + "<label class='form-check-label' for='flexCheckDefault'></label>"
    + "</div>"
    + "</th>"
    + "</tr>"
    + "</thead>"
    + "<tbody>";

    new_data = [];
    for (i=0;i<data.dictionary[varName].values.length;i++){
        content_html += 
        "<tr>"
        + "<td>"+ data.dictionary[varName].values[i] +"</td>"
        + "<td class='text-center center-block selectable-cell'></td>"
        + "</tr>";
    }

    content_html += 
    "</tbody>"
    + "</table>";

    $("#"+varName)[0].innerHTML = content_html;

 }

/**
 * Function that initializes/declare the table that contains the categories. 
 */
function initializeRefreshTableCategories(){

    // DataTable table_categories. Checkbox column in position 1, multishift selection style. 
    // The checkbox for selection is in the last column of the table.
    var table = $("#table_categories").DataTable({

        // Pagination, labels and other options
        paging: true,
        language: {
            search: "Buscar:",
            lengthMenu: "Mostrar _MENU_ entradas",
            info: "Mostrando _START_ hasta _END_ de un total de _TOTAL_ entradas",
            paginate: {
                next:       "Siguiente",
                previous:   "Anterior"
            },
        },

        // disable default alphabetical order
        order: [],

        // set up of the position of the Datatable desired elements (search bar, length info...)
        dom: "<'row'<'col-sm-12 col-md-6'f><'col-sm-12 col-md-6'p>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'i>>",

        // Selectable columns management
        columnDefs: [ 
            {
                orderable: false,
                className: 'select-checkbox',
                targets:   1,
            },

        ],
        select: {
            style:    'multi+shift',
            selector: 'td:nth-last-child(1)',
        },

    });

    // Event listeners on the table, triggered when a row is selected/deselected
    table
        .on( 'select', function () {

            varName = this.parentElement.parentElement.parentElement.parentElement.id;
            categoriesTableSelectedDeselected("select", varName);

        } )
        .on( 'deselect', function () {

            varName = this.parentElement.parentElement.parentElement.parentElement.id;
            categoriesTableSelectedDeselected("deselect", varName);

        } )
        .on( 'search.dt', function () {
            // Update the selection button so the user can select or deselect all variables correctly
            UpdateSelectionBox();
        } );

}

/**
 * Function that manages the global variable linked to the Table of Categories when a category or row is (de)selected
 */
 function categoriesTableSelectedDeselected(option, varName){

    if (option == "select"){
        get_selected = true;
    }
    else{
        get_selected = false;
    }

    // get all categories of the variable
    categories = $("#table_categories").DataTable().columns(0).data()[0];

    // get (de)selected rows indexes
    indexes = $("#table_categories").DataTable().rows( { selected: get_selected } ).indexes();

    // set those categories to true/false in the global variable
    for (i=0; i<indexes.length; i++){
        selectedCategoriesDictionary[varName][categories[indexes[i]]] = get_selected;
    }

    // refresh the select all checkbox
    UpdateSelectionBox();

    refreshFiltersInformation();

 }

/**
 * Function that checks if all rows are selected or not, so the user can select or deselect all variables
 */
function UpdateSelectionBox() {

    table = $("#table_categories").DataTable();

    // get the searched rows (the ones that are currently on screen) and the selected rows
    searched_rows = table.rows({ search: 'applied' })[0];
    selected_rows = table.rows( { selected: true } )[0];

    // if all the rows in the screen are selected, check the box
    if (searched_rows.every(r => selected_rows.includes(r))){
        
        $( "#select_deselect_all" ).prop('checked', true);

    }

    // if not, uncheck the box
    else{
        $( "#select_deselect_all" ).prop('checked', false);
    }

}

/**
 * Function that selects all the variables that are currently visible for the user (search filtering applied)
 */
function selectAllListener(){

    // user just clicked it and now it's checked (user wants to select all rows)
    if ($( "#select_deselect_all" )[0].checked){

        // select the variables that matches with the previous indexes
        $('#table_categories').DataTable().rows({ search: 'applied' }).select();

    }

    // user just clicked it and now it's unchecked (user wants to deselect all rows)
    else{

        // deselect the variables that matches with the previous indexes
        $('#table_categories').DataTable().rows({ search: 'applied' }).deselect();

    }

}

/**
 * Function that generates the HTML code related to the summary of the selected categories of the user
 */
 function getTableCategoriesFiltersInformationHTML(){

    // header and structure of the table
    table_categories_info_string = 
      "<table class='table table-striped'>"
    + "<thead>" 
    + "<tr>"
    + "<th>Variable categórica</th>"
    + "<th>Categorías seleccionadas</th>"
    + "<th>Categorías no seleccionadas</th>"
    + "</tr>"
    + "</thead>"
    + "<tbody>";

    // body of the table, get the selected and not selected categories of each variable in the global dictionary
    for (const [var_name, selected_cat_dict] of Object.entries(selectedCategoriesDictionary)) {

        table_categories_info_string += "<tr>";

        selected_string = "";
        non_selected_string = "";
        for (const [category, selected] of Object.entries(selected_cat_dict)) {
            if (selected){
                selected_string += category + ", ";
            }
            else{
                non_selected_string += category + ", ";
            }
        }

        // remove last comma
        selected_string = selected_string.slice(0, -2)
        non_selected_string = non_selected_string.slice(0, -2)

        // add information
        table_categories_info_string +=
          "<td>" + var_name + "</td>"
        + "<td>" + selected_string + "</td>"
        + "<td>" + non_selected_string + "</td>"
        + "</tr>";

    }

    // finish the structure of the table
    table_categories_info_string +=
      "</tbody>"
    + "</table>";

    return table_categories_info_string;
}

/// *** Functions for managing Numerical Intervals ***

/**
 * Function that generates the numerical filter (button for the creation of intervals and crceates the intervals automatically in case they
 * were defined previously)
 */
function generateNumericalFilter(varName, data){

    // Get the maximum and minimum value of the numeric variable (info in the dictionary from the API call) 
    min_value = data.dictionary[varName]['values'][0]['min'];
    max_value = data.dictionary[varName]['values'][0]['max'];

    // generate the HTML code for the section where the intervals of the current variable are going to be added
    generateIntervalsSectionHtml(varName);

    // if the intervals of the variable had been set up previously, build them as before
    if (varName in selectedIntervalsDictionary){

        // iterate over all the previously built intervals
        for ([key, value] of Object.entries(selectedIntervalsDictionary[varName])) {       
            generateIntervalPrevious(varName, parseInt(key.charAt(key.length-1)), value[0], value[1], [min_value, max_value]);
        }

    }

    // delete the previous event listeners
    $('.interval-generator-button').off(); 

    // Click event that that creates an Interval when the button "Nuevo Intervalo" is clicked
    $('.interval-generator-button').on('click', generateIntervalNew);

}

/**
 * Function that generates the HTML code for the section where the intervals of the current variable are going to be added
 */
function generateIntervalsSectionHtml(varName){

    // Get the reference to the space for the intervals of this variable
    parent_node = $("#"+varName)[0];

    // Add the correct html to this section
    content_html = 
        "<b>Definición de intervalos para la variable "+varName+"</b>"+" (valores entre "+String(min_value)+" y "+String(max_value)+")"
        + "<br/><br/>"
        + "<button type='button' class='btn btn-primary btn-lg interval-generator-button'>Nuevo Intervalo</button>"
        + " (Máximo 5 intervalos distintos)"
        + "<br/><br/>"
        + "<div id='Interval_container" + "' class='" + String(min_value) + "_" + String(max_value) + "'></div>";

    parent_node.innerHTML = content_html;

}

/**
 * Function that generates all previous intervals built by the user and linked to the current variable
 */
 function generateIntervalPrevious(varName, intervalId, lower_interval_value, upper_interval_value, min_max){

    // create the structures for the function calling
    interval_info = {"interval_number":intervalId};
    interval_values = {"lower_interval_value":lower_interval_value, "upper_interval_value":upper_interval_value};

    // call the function that will generate the Interval Html code
    generateIntervalHtml(interval_info, interval_values, min_max, "previous");

    // refresh the listeners related with the interval (remove button and numeric input)
    refreshIntervalListerers();

    // Add information of the filters to the screen
    refreshFiltersInformation();

}

/**
 * Function that generates a new interval of the current selected variable (up until 5)
 */
 function generateIntervalNew(){

    // Get number of intervals of the selected variable
    child_count = $("#Interval_container")[0].childElementCount

    if (child_count < 5){

        // get the maximum and minimum value that can take the variable, based on the class ("min_max -> class='0_10'")
        min_max = $("#Interval_container")[0].className.split("_");

        // get the value of the new interval based on the values of it previous and following intervals
        interval_info = getCurrentPreviousIntervalInfo(child_count);        

        // get the values of the lower and upper interval based on the values of the previous and next intervals
        interval_values = getLowerUpperValuesInterval(interval_info, min_max);

        // generate the html content of the new interval based on the interval number previously calculated
        generateIntervalHtml(interval_info, interval_values, min_max, "new");

        // Add the variable to the intervals dictionary if it is not initialized
        if (!(varName in selectedIntervalsDictionary)){
            selectedIntervalsDictionary[varName] = {};
        }

        // Add the interval to the global variable, bound to the current selected variable
        selectedIntervalsDictionary[varName]["Interval_"+String(interval_info["interval_number"])] = [interval_values["lower_interval_value"],
        interval_values["upper_interval_value"]];

        // refresh the listeners related with the interval (remove button and numeric input)
        refreshIntervalListerers();

        // Add information of the filters to the screen
        refreshFiltersInformation();

    }
}

/**
 * function that will generate the Interval Html code. The option parameter will clarify if we're building a previous or new interval
 */
function generateIntervalHtml(interval_info, interval_values, min_max, option){

    // get the html content based on the interval number previously calculated
    content_html =
    "<div id='Interval_" + String(interval_info["interval_number"]) + "'"  
    + "<br/>"
    + "<b>Intervalo " + String(interval_info["interval_number"]+1) + ":&nbsp;</b>"
    + "<div class='interval-box'><input type='number' class='interval lower-interval' value='"+ interval_values["lower_interval_value"]
    + "' min='" + String(min_max[0]) + "' max='" + String(min_max[1]) + "'></div>"
    + "<div class='hyphen'>-</div>"
    + "<div class='interval-box'><input type='number' class='interval upper-interval' value='"+ interval_values["upper_interval_value"]
    + "' min='" + String(min_max[0]) + "' max='" + String(min_max[1]) + "'></div>"
    + "<div class = 'remove-interval'><i class = 'far fa-times-circle close-icon-trigger'></i></div>"
    + "</div>";

    

    // insert the html code in the correct position, depending on if it is a new interval or a previous built one
    if (option == "new"){
        
        if (interval_info["previous_interval_number"] == -1){
            $("#Interval_container")[0].innerHTML = content_html + $("#Interval_container")[0].innerHTML;
        }
        else{
            $("#Interval_container")[0].children[interval_info["previous_interval_number"]].after($(content_html).get(0));
        }
    }

    else if(option == "previous"){
        $("#Interval_container")[0].innerHTML += content_html
    }
    
}

/**
 * function that refreshes all the listeners bound to the clicked/modified interval
 */
function refreshIntervalListerers(){

    // Refresh the delete interval listeners
    $('.remove-interval').off(); 
    $('.remove-interval').on('click', removeInterval);

    // Refresh the interval modifier listeners
    $('.interval').off();
    $('.interval').on('mouseup', numericInputChanged);
    $('.interval').on('keyup', numericInputChanged);

}

/**
 * function that removes the interval whose deletion button has been clicked 
 */
function removeInterval(){

    // get the name of the variable and the interval
    varName = this.parentElement.parentElement.parentElement.id
    interval_id = this.parentElement.id

    // delete the interval object from the global var (dict with an array with lower and upper interval's values)
    delete selectedIntervalsDictionary[varName][interval_id]

    // if the dict of the variable remains without any interval, remove it from the global variable
    if (Object.keys(selectedIntervalsDictionary[varName]).length == 0){
        delete selectedIntervalsDictionary[varName]
    }

    refreshFiltersInformation();

    // remove the whole interval html object
    this.parentElement.remove()

}

/**
 * Function that will be bound to the interval input's event listeners, updates the value of the numeric intervals global variable
 */
function numericInputChanged(){

    // get the variable and the number/id of the interval, so we can actualize the value of the global variable correctly
    varName = this.parentElement.parentElement.parentElement.parentElement.id;
    interval_id = this.parentElement.parentElement.id;

    // change the value keeping in mind if it is lower or upper interval
    if (this.classList[1] == 'lower-interval'){
        selectedIntervalsDictionary[varName][interval_id][0] = this.value;
    }
    else if (this.classList[1] == 'upper-interval'){
        selectedIntervalsDictionary[varName][interval_id][1] = this.value;
    }

    refreshFiltersInformation();

}

/**
 * Function that gets where the interval should be inserted, which is the previous interval and the ids of the rest of the current intervals
 */
function getCurrentPreviousIntervalInfo(child_count){

    // get the first available interval number (if user has intervals 1,2 and 4, build the interval 3)
    non_available_numbers = [];
    for (i=0; i<child_count; i++){
        non_available_numbers.push(
            parseInt($("#Interval_container")[0].children[i].id.charAt(
                    $("#Interval_container")[0].children[i].id.length - 1)
            )
        );
    }
    interval_number = [0,1,2,3,4].filter(value => !non_available_numbers.includes(value))[0];

    // get the place where the interval is going to be inserted so it is in correct order
    previous_interval_number = -1;
    for (i=0; i<non_available_numbers.length; i++){
        if (interval_number > non_available_numbers[i]){
            previous_interval_number = i;
        }
    }

    // build the return value that contains the current interval number and the number of the previous interval
    interval_info = {}
    interval_info["interval_number"] = interval_number;
    interval_info["previous_interval_number"] = previous_interval_number;
    interval_info["non_available_numbers"] = non_available_numbers;

    return interval_info;

}

/**
 * Function that gets the values of the new interval to be inserted, based on the values of the previous and followinf intervals
 */
function getLowerUpperValuesInterval(interval_info, min_max){

    // lower interval (min if its the first interval, max of the previous interval if not)
    if (interval_info["previous_interval_number"] == -1){
        lower_interval_value = String(min_max[0])
    }
    else{
        lower_interval_value = $("#Interval_container")[0].children[interval_info["previous_interval_number"]].children[3].children[0].value
    }

    // upper interval 
    // if there is not any interval or the interval is the last one in the list of Intervals, the upper interval value will
    // be the max value of the variable
    if ((interval_info["non_available_numbers"].length == 0) || 
    (interval_info["previous_interval_number"] == interval_info["non_available_numbers"].length-1)){
        upper_interval_value = String(min_max[1])
    }
    // if it has a subsequent interval, take its lower interval as value 
    else{
        upper_interval_value = $("#Interval_container")[0].children[interval_info["previous_interval_number"]+1].children[1].children[0].value
    }

    // build the return value
    interval_values = {}
    interval_values["lower_interval_value"] = lower_interval_value
    interval_values["upper_interval_value"] = upper_interval_value

    return interval_values;
}

/**
 * Function that generates the HTML code related to the summary of the created intervals by the user
 */
function getIntervalFiltersInformationHTML(){

    // header and structure of the table
    intervals_info_string = 
      "<table class='table table-striped'>"
    + "<thead>" 
    + "<tr>"
    + "<th>Variable numérica</th>"
    + "<th>Intervalos creados</th>"
    + "</tr>"
    + "</thead>"
    + "<tbody>";

    // body of the table, get the selected and not selected categories of each variable in the global dictionary
    for (const [var_name, selected_interval_dict] of Object.entries(selectedIntervalsDictionary)) {

        intervals_info_string += "<tr>";
        selected_intervals_string = "";
        for (const [int_number, interval_arr] of Object.entries(selected_interval_dict)) {
            selected_intervals_string += "[" + interval_arr[0] + ", " + interval_arr[1] + "], "
        }

        // remove last comma
        selected_intervals_string = selected_intervals_string.slice(0, -2)

        // add information
        intervals_info_string +=
          "<td>" + var_name + "</td>"
        + "<td>" + selected_intervals_string + "</td>"
        + "</tr>";

    }

    // finish the structure of the table
    intervals_info_string +=
      "</tbody>"
    + "</table>";

    return intervals_info_string;

}

// *** Other functions that act as tools that helps both modules: Table of categories and Numerical Intervals ***

/**
 * Function that refreshes an area in the HTML side with the current information in both global variables: Table of Categories
 * and Numeric Intervals
 */
function refreshFiltersInformation(){

    // get the HTML related to the summary of the selected categories of the user
    table_categories_info_string = getTableCategoriesFiltersInformationHTML();

    // get the HTML related to the summary of the created intervals by the user
    intervals_info_string = getIntervalFiltersInformationHTML();

    $("#filter_information")[0].innerHTML = 
        "<h5>Variables <b>categóricas</b>:</h5>"
        + "<br/><br/>"
        + table_categories_info_string
        + "<br/>"
        + "<h5>Variables <b>numéricas</b>:</h5>"
        + "<br/><br/>"
        + intervals_info_string;

}
    