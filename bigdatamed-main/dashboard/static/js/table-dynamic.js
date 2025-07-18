// initialize global variables

// initialize the value of the div that contains the selected variables
$("#selected_vars_div").html("<strong>No hay variables seleccionadas</strong>");

// csrftoken initial configuration

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

// This variable will contain a random color for each category of the selectmenu codified in a dictionary
var categoryColors;

/**
 * document ready function, runs functions once the web (DOM) is fully loaded
 */
$(document).ready(function() {

    // DataTable table_dynamic. Custom paging with Django, Checkbox column in position 2, multishift selection style. The checkbox for selection is in the last column of the table (pos 2).
    var table = $("#table_dynamic").DataTable({

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
                targets:   4,
            },
            {
                orderable: false,
                targets:   5,
            },

        ],
        select: {
            style:    'multi+shift',
            selector: 'td:nth-last-child(2)',
        },
    });

    // These functions are called when a row in the datatable table_dynamic is selected or deselected
    table
        .on( 'select', function ( ) {
            UpdateSelectedVariables();
            refreshVariableListeners();   
        } )
        .on( 'deselect', function ( ) {
            UpdateSelectedVariables();
            refreshVariableListeners();   
        } )
        .on( 'search.dt', function () {
            // Update the selection button so the user can select or deselect all variables correctly
            UpdateSelectionBox();
        } );

    $( "#category_menu" ).selectmenu(
        {
            // this function will be triggered when the user selects a category from the selectmenu
            change: function( event, data ) 
                    {

                        // Get the selected category that will toggle the filter of the DataTable
                        selected_category = data.item.value;
                        table = $('#table_dynamic').DataTable();

                        if (selected_category == "Cualquiera"){

                            // show all data
                            table.search( '' ).columns().search( '' ).draw();

                        }
                        else{

                            // Get the column where the data is going to be searched -> class of the menu
                            col_name = $( "#category_menu" )[0].classList[0]
                            
                            // get the index of this column in the table
                            selected_index = 0
                            for (i = 0; i < $('#dynamic_table').dataTable().dataTableSettings[0].aoColumns.length; i++){
                                if (col_name == $('#dynamic_table').dataTable().dataTableSettings[0].aoColumns[i].sTitle){
                                    selected_index = i
                                }
                            }

                            // show only the selected category
                            table.columns( selected_index ).search( selected_category ).draw();

                        }
                        
                    },

                // create and populate the category colors when the selectmenu that contains the categories is created
                create: function( event, ui ) {

                    // initialize and populate the dictionary
                    categoryColors = {};
                    for (i=0; i<$( "#category_menu" )[0].length-2;i++){
                        categoryColors[$( "#category_menu" )[0][i+2].text] = randomHSL();
                    } 

                }
        }
    );

});

/**
 * Function that selects all the variables that are currently visible for the user (search filtering applied)
 */
 $("#select_deselect_all").on('click', function(){

    // user just clicked it and now it's checked (user wants to select all rows)
    if ($( "#select_deselect_all" )[0].checked){

        // select the variables that matches with the previous indexes
        $('#table_dynamic').DataTable().rows({ search: 'applied' }).select();

    }

    // user just clicked it and now it's unchecked (user wants to deselect all rows)
    else{

        // deselect the variables that matches with the previous indexes
        $('#table_dynamic').DataTable().rows({ search: 'applied' }).deselect();

    }

});

/**
 * Function that calls the plot function when clicking on the eye of a row and provides the name of the variable that must be plotted and the type of it
 */
$('.show_chart').on('click', function(){

    // store a reference to the clicked row, that has the info of the variable that is going to be plotted
    context_row = $(this)[0];
    context_row.parentElement.children[5].children[0].outerHTML = "<div class='spinner-border' role='status'></div>";

    // call the plot variable function, that alse receives the reference to the selected row of the table
    plotVariable($(this)[0].parentElement.firstElementChild.outerText, $(this)[0].parentElement.children[3].outerText, context_row);
});

/**
 * Function that refreshes de click events of the selected variable's labels
 */
function refreshVariableListeners(){

    // delete the previous event listeners
    $('.close-icon-trigger').off(); 

    // Click event that deselects a variable when the label's close icon is clicked 
    $('.close-icon-trigger').on('click', function(){

        // Access to the variable that the user wants to deselect
        varName = this.parentNode.parentNode.childNodes[1].textContent;

        table = $('#table_dynamic').DataTable();

        $('#table_dynamic').DataTable().rows(
            function ( idx, data, node ) {
                return data[0] === varName;
            }
        ).deselect();

    });

}

/**
 * Function that calls the plot function when clicking on the eye of a row. It gets as parameters the name of the variable, its type and a
 * reference to the row of the selected variable in the datatable
 */
function plotVariable(varToPlot, varType, contextRow){

    // address where the POST request is going to be sent (Django View)
    address = window.location.origin + '/ajax/plot_variable';

    // Ajax POST request
    $.ajax({
        url: address,
        cache:'false',
        dataType: 'json',
        type:"POST",
        data: {"new_variable": varToPlot, "var_type":varType},
        headers:{
            "X-CSRFToken": csrftoken
        },
        async: true,
        success: function(data){

            // if the function successes, there will be a field called success that have been set to true in the Django view
            if (data.success){

                // A new chart is going to be added, because a new variable has been selected, call the function createChart
                createChart(data, contextRow);
                    
            }
            else{
                alert("error: data didn't success");
            }
            
        },
        error: function(){
            alert('error; '+ eval(error));
        }
    });

}

/**
 * Function that updates the html section that shows the variables that are currently selected
 */
function UpdateSelectedVariables() {
    
    table = $("#table_dynamic").DataTable()
    
    // get the selected variables and keep the names on a list
    selected_data = table.rows( { selected: true } ).data()

    // get the variables and sort them by categories so the colors are grouped correctly
    selected_vars = [];
    var_categories = [];
    
    for (let i = 0; i < selected_data.length; i++) {
        selected_vars.push(selected_data[i][0]);
        var_categories.push(selected_data[i][2]);   
    }

    // get the indices sorted and map the order of the arrays based on those indices
    indices_sorted = Array.from(var_categories.keys()).sort( (a,b) => var_categories[a].localeCompare(var_categories[b]) );
    selected_vars = indices_sorted.map(i => selected_vars[i]);
    var_categories = indices_sorted.map(i => var_categories[i]);
   
    // save in a list the categories that the user have selected until the current instant
    variable_selected_list = []
    category_list = var_categories.slice()
    category_list = jQuery.uniqueSort(category_list)
    
    // build every single label with its correct color and text
    content_html = "<strong>Variables seleccionadas: </strong><br/><br/>";
    for (let i = 0; i < selected_vars.length; i++) {
        content_html = content_html + "<div class = 'variable-container'><div class = 'variable-label'>" +
        "<div class = 'circle-category-container'><i class = 'fas fa-circle' style='color:" + categoryColors[var_categories[i]]
        + ";font-size:0.7rem;'></i></div>" + selected_vars[i] +
         "<div class = 'close-icon'><i class = 'far fa-times-circle close-icon-trigger'></i></div></div></div>";

         // create a dictionary with the selected variable and its category and then add it to a list with the selected variables
         dictionary = {};
         dictionary[selected_vars[i]]=var_categories[i];
         variable_selected_list.push(dictionary);
    }

    // Show selected variables (label with color and name) in HTML
    $("#selected_vars_div").html(content_html);
    
    content_html_var = ""
    content_html_cat = ""
   
    // build a string that contains the names of the variables and their categories
    content_html_var = getKeyDictionaryFromList(variable_selected_list);

    // build a string with the categories
    for (let  i=0; i < category_list.length; i++){
        content_html_cat += category_list[i] + ",";
    }

    // remove last comma
    content_html_cat = content_html_cat.slice(0, -1)

    // populate session variables
    $("#request-variable-selected")[0].value = content_html_var
    $("#request-category-selected")[0].value = content_html_cat
    
    UpdateSelectionBox();
    
}

/**
 * Function get KeyValue Dictionary with list dictionary with params.
 * From list of dictionaries to a string: ["Hospital":"Básico", "C1":"Diagnóstico"] -> "{ HOSPITAL|Básico }, { C1|Diagnóstico }"
 */
function getKeyDictionaryFromList(list_dict){

    // initialize the output string
    let content_html = "";

    // iterate all over selected variables (in a list of dictionaries)
    for (let  i=0; i < list_dict.length; i++){

        // get the key (name of the variable) and the value (category of the variable) out of the dictionary and add it to the ourput string
        Object.keys(list_dict[i]).forEach(function eachKey(key){clave = key; valor = list_dict[i][key]});
        content_html += "{ " + clave +"|"+valor + " }, "; 
    }

    // remove last comma and space of the string
    content_html = content_html.slice(0, -2)
    
    return content_html;
}

/**
 * Function that checks if all rows are selected or not, so the user can select or deselect all variables
 */
 function UpdateSelectionBox() {

    table = $("#table_dynamic").DataTable();

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
 * Function that creates a new Chart of ChartJS and generates the necessary html code to render it. It also generates a dialog box.
 * Param data: data required to create the ChartJS plot
 */
function createChart(data, contextRow) {

    // set the default witdh and height of the chart 
    width_size_chart = "auto"
    height_size_chart = ($(window).height() * 0.85)-57

    // Depending on the variable type, call the function for getting the configuration of a chart for categorical variables or numerical ones
    if (data["data_dict"]["var_type"] == "Categorical"){

        config_chart = configCategoricalChart(data);

    }

    else if (data["data_dict"]["var_type"] == "Numerical"){

        config_chart = configNumericalChart(data);

        // modify the witdh and height of the chart if it's a numerical variable
        width_size_chart = $(window).width() * 0.5
        height_size_chart = "auto"

    }

    // remove previous charts and chart variables
    $('#ChartVariable').remove();

    // remove the loading spinner
    contextRow.parentElement.children[5].children[0].outerHTML = "<i class='fas fa-eye'></i>";

    // create the dialog
    $("#dynamic_dialog").dialog({
        resizable: false,
        draggable: false,
        width: width_size_chart,
        height: height_size_chart,
        show: "fade", // animation
        modal: true, // don't let the user interact with the rest of the elements of the view

        // function that manages what happends when the dialog function is opened
        open: function (event, ui) {

            // remove default classes of dialog button
            $(this).next().find("button").removeClass("ui-button ui-corner-all ui-widget");

            // create the canvas and the chartjs plot
            $("#dynamic_dialog").append("<canvas id='ChartVariable'></canvas>")
            current_chart = new Chart(
                $('#ChartVariable'),
                config_chart
            );    

            // adjust the size of the canvas to the size of the dialog box
            $("#ChartVariable").css("width",'auto');
            $("#ChartVariable").css("height",'100%');     

        },

        create: function( event, ui ) {

            // set the css characteristics of the dialog before it is opened
            $("#dynamic_dialog").parent().css('top', '50%')
            $("#dynamic_dialog").parent().css('left', '50%')
            $("#dynamic_dialog").parent().css('z-index', '101')
            $("#dynamic_dialog").parent().css('position', 'fixed')
            $("#dynamic_dialog").parent().css('transform', 'translate(-50%, -50%)')

        },

        // set up the close button
        buttons: [
            {
              text: "Cerrar Ventana",
              click: function() {
                $( this ).dialog( "close" );
              },
              class: "btn btn-primary btn-lg"
            }
        ],
    });
        
}

/**
 * Function that generates a random pastel color
 */
function randomHSL(){
    return "hsla(" + ~~(360 * Math.random()) + "," + "70%,"+ "80%,1)";
}

/**
 * Function that returns the needed configuration for plotting a doughtnut Chartjs chart for categorical variables
 */
function configCategoricalChart(data){

    random_colors = [];
    // generate random pastel colors
    for (let i=0; i < data["data_dict"]["labels"].length; i++){
        random_colors.push(randomHSL());
    }
    
    // data for chart of ChartJS
    data_chart = {
        labels: data["data_dict"]["labels"],
        datasets: [{
            data: data["data_dict"]["data"],
            backgroundColor: random_colors,
        }]
    };

    // config object for the chart of ChartJS
    config_chart = {
        type: 'doughnut',
        data: data_chart,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Resumen de los valores de la variable ' + data["data_dict"]["var_name"]
                },
                legend: {
                    position: "top",
                }
            },  
        },
        responsive: true,
        maintainAspectRatio: true,
    };

    return config_chart;

}

/**
 * Function that returns the needed configuration for plotting a doughtnut Chartjs chart for categorical variables
 */
 function configNumericalChart(data){

    // configuration og the variable that will have a list of the X, Y and label parameters of each histogram's interval
    data_array_histogram = [];

    // Fake first point so the histogram can begin at 0.5 in the x-axis (no label and no y-value)
    data_array_histogram.push({x: 0.5, label: '', y: 0});

    // insert all the histogram points from the API response data: x:0.5 per each value, label: bin label, y: number of elements of that interval
    for (i = 1; i < data["data_dict"]["histogram_data"].length; i++){
        data_array_histogram.push({x: i+0.5, label: data["data_dict"]["histogram_bins"][i-1], y: data["data_dict"]["histogram_data"][i-1]});
    }

    // data for chart of ChartJS
    data_chart = {
        labels: data["data_dict"]["histogram_bins"],
        datasets: [{
            label: 'Número de elementos en el rango de valores',
            data: data_array_histogram,
            backgroundColor: randomHSL(),
            barPercentage: 1,
            categoryPercentage: 1,
            borderWidth: 0.6,
            borderColor: 'rgb(50, 50, 50)',
            borderRadius: 5
        }]
    };

    // config object for the chart of ChartJS
    config_chart = {
        type: 'bar',
        data: data_chart,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Histograma con el resumen de los valores de la variable ' + data["data_dict"]["var_name"]
                },
                legend: {
                    display: false,
                },
                tooltip: {

                    // text that appears when the user places the cursor on a bar of the histogram (edge values of the histogram's interval)
                    callbacks: {
                        
                        title: (items) => {

                            // if the interval is not the last one, pick the current value and the next one in the array to build the text
                            if (items[0].dataIndex+1 == data_array_histogram.length){
                                return "Intervalo [" + data_array_histogram[items[0].dataIndex]["label"].toString() 
                                + " , " + data["data_dict"]["histogram_bins"][data["data_dict"]["histogram_bins"].length-1].toString() + ")"
                            }

                            // if the interval is the last one, pick the current value and the last label of the response data of the API
                            return "Intervalo [" + data_array_histogram[items[0].dataIndex]["label"].toString() 
                            + " , " + data_array_histogram[items[0].dataIndex+1]["label"].toString() + ")"
                        }
                    }
                }
            },
            scales: {

                // x scale set up
                x:{
                    // set of the histogram plot and the grid
                    type: 'linear',
                    offset: false,
                    grid: {
                        offset: false
                    },

                    // bins will have size 1, but all will have their label
                    ticks: {
                        stepSize: 1,

                        // set up of each value of the X axis (lower and upper part of each interval)
                        callback: function(val, index) {
                            if (index == data_array_histogram.length){
                                return data["data_dict"]["histogram_bins"][data["data_dict"]["histogram_bins"].length-1]
                            }
                            return data_array_histogram[index]['label'];
                        },
                    },

                    // title of x-axis
                    title: {
                        display: true,
                        text: data["data_dict"]["var_name"]
                    }
                },
                y: {

                    // title of y-axis
                    title: {
                        display: true,
                        text: "Número de elementos"
                    }
                }
            }
        },
        responsive: true,
        maintainAspectRatio: true,
    };

    return config_chart;

}