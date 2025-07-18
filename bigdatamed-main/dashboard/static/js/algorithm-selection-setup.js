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

    // set up the selectmenu with the names of the available algorithms
    $( "#algorithm_menu" ).selectmenu(
        {
            // generate the form with the parameters associated to the new selected algorithm
            change: function( event, data ) {
                
                generateInfoParamsAlgorithm(this.className);

            },

            // generate the form with the parameters associated to the algorithm selected by default, when the selectmenu is created
            create: function( event, ui ) {

                generateInfoParamsAlgorithm(this.className);

            }
        }
    );

});

/**
 * Function that generates an ajax POST request for updating the parameters of the selected algorithm in the form
 * The problem String will contain Clustering, Clasificacion, Regresion or EDA
 */
function generateInfoParamsAlgorithm(problemString){

    // Ajax POST request that gets the info about the parameters of the available algorithms
    $.ajax({
        url: window.location.origin + '/ajax/get_info_parameters_algorithm',
        cache:'false',
        dataType: 'json',
        type:"POST",
        data: {"problem_string": problemString},
        headers:{
            "X-CSRFToken": csrftoken
        },
        async: true,
        success: function(data){

            // if the function successes, generate the HTML
            if (data.success){
                generateAlgorithmForm(data['algorithm_parameters'][$('#algorithm_menu').val()]);
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

/**
 * Function that generates the HTML form and calls the function that generates the HTML section for every parameter of the algorithm
 */
function generateAlgorithmForm(algorithmParametersInfo){
    
    content_html = "<form id='algorithmParametersForm'>";

    // for every parameter of the algorithm, generate its form HTML code 
    for (const [param_name, param_info] of Object.entries(algorithmParametersInfo)) {
        content_html += generateParameterHTML(param_name, param_info, false);
    }

    // add the form label
    content_html += "</form>";

    $("#algorithm_parameters")[0].innerHTML = content_html;

    // refresh the listener of the distributed run of the algorithm checkbox
    refreshDistributedCheckboxListener();

    // refresh the listener for the elbows method in case the current algorithm is KPrototypes
    refreshElbowMethodListener(algorithmParametersInfo);

}

/**
 * Function that generates the HTML form code associated to any kind of variable.
 * distributedParameters will add the distributed class to the labels div if is set to true
 */
function generateParameterHTML(parameterName, parameterInfo, distributedParameters){

    // Add the row associated to the current parameter to the horizontal main form
    // if the distributedParameters flag is true, add the class to the div
    if (distributedParameters){
        content_html_parameter = "<div class='form-group row" + parameterInfo["data"][0] + " distributedParameter'>";
    }
    else{
        content_html_parameter = "<div class='form-group row" + parameterInfo["data"][0] + "'>";
    }

    // If the parameter is not boolean, set the label for the parameter
    if (parameterInfo["data"][0] != "Boolean"){
        if (parameterInfo["doc"] == ""){
            content_html_parameter += "<label for='" + parameterName + "' class='col-sm-2 col-form-label'>" + parameterName + "</label>";
        }
        else{
            content_html_parameter += "<label for='" + parameterName + "' class='col-sm-2 col-form-label'>" + 
            "<span class='hovertext' data-hover='" + parameterInfo["doc"] + "'>" + parameterName + "</span>" + "</label>";   
        }
    }

    // Choice: parameter type, array of choices (first one will be the default option)
    if (parameterInfo["data"][0] == "Choice"){

        content_html_parameter += "<select class='form-control'>";
        
        // Add all the choices as options
        for (i=0; i<parameterInfo["data"][1].length;i++){
            content_html_parameter += "<option>"+ parameterInfo["data"][1][i] + "</option>";
        }
        content_html_parameter += "</select>";
    }

    // Integer/Float: parameter type, default value, min value (optional), max value (opyional)
    else if (parameterInfo["data"][0] == "Integer" || parameterInfo["data"][0] == "Float"){

        // set the input type number label
        content_html_parameter += "<input type='number' value='" + parameterInfo["data"][1] + "'";

        // if the default value of an integer/float is null, set the parameter to an empty string
        if (parameterInfo["data"][1] == null){
            parameterInfo["data"][1] = ""
        }

        // check for min and max (if length is 3 it will only contain a minimum value, which is the most common one)
        if (parameterInfo["data"].length == 3){
            content_html_parameter += " min='" + parameterInfo["data"][2] + "'";
        }
        else if(parameterInfo["data"].length == 4){
            content_html_parameter += " min='" + parameterInfo["data"][2] + "' max='" + parameterInfo["data"][3] + "'";
        }

        // if the parameter is a float, set the step to the last decimal. 
        if (parameterInfo["data"][0] == "Float"){
            
            // if it contains a ., set the step to a last decimal and if not, set the step to 0.1
            if (String(parameterInfo[1]).includes(".")){
                step = String(parameterInfo[1]).slice(0, -1) + "1";
            }
            else{
                step = 0.1;            
            }
            content_html_parameter += "step = '" + step + "'";
        }

        content_html_parameter += "</input>";
    }

    // Boolean: parameter type, default value (True or False). Check for the reserved word in the parameter name "distributedExecution", 
    // which has a special class 
    else if (parameterInfo["data"][0] == "Boolean"){
        
        content_html_parameter += "<div class='form-check'>" + "<input class='form-check-input";

        if (parameterName == "distributedExecution"){
            content_html_parameter += " distributedCheckbox";
        }

        content_html_parameter += "'type='checkbox' value='' id='" + parameterName + "'></input>" 
        + "<label class='form-check-label' for='" + parameterName + "'>";

        if (parameterInfo["doc"] != ""){
            content_html_parameter += "<span class='hovertext' data-hover='" + parameterInfo["doc"] + "'>" 
            + parameterName + "</span>";
        }
        else{
            content_html_parameter += parameterName;
        }

        content_html_parameter += "</label></div>";

    }

    // String: parameter type, default value (a string)
    else if (parameterInfo["data"][0] == "String"){
        
        // set a input type string
        content_html_parameter += "<input type='text' value='" + parameterInfo["data"][1] + "'";

    }

    content_html_parameter += "<br></div>";

    return content_html_parameter;
}

/**
 * Function that refreshes and establishes what happens when the users check the box of the distributed execution.
 * Parameters of the distributed execution are added/removed
 */
function refreshDistributedCheckboxListener(){

    // turn off the previous listeners
    $('.distributedCheckbox').off(); 

    // set up the new listener on the elements of this class
    $(".distributedCheckbox").on('click', function(){

        // if the checkbox has just been checked, add the parameters for the distributed execution to the form
        if (this.checked){

            // Ajax POST request that gets the parameters for a distributed execution
            $.ajax({
                url: window.location.origin + '/ajax/get_distributed_parameters',
                cache:'false',
                dataType: 'json',
                type:"POST",
                data: {},
                headers:{
                    "X-CSRFToken": csrftoken
                },
                async: true,
                success: function(data){

                    // if the function successes, add the new parameters to the algorithm form
                    if (data.success){

                        content_html = ""
                        // for every parameter, generate its form HTML code . They will have the class distributedParameter so they can be 
                        //removed in case the user uncheck the checkbox
                        for (const [param_name, param_info] of Object.entries(data["distributed_parameters"])) {
                            content_html += generateParameterHTML(param_name, param_info, true);
                        }
                        
                        // add the new parameters to the algorithm form
                        $("#algorithmParametersForm").append(content_html)
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

        // if the checkbox has just been unchecked, remove the parameters for the distributed execution from the form
        else{
            
            // remove the parameters
            $(".distributedParameter").remove()

        }

    });
}


/**
 * Function that handles the event listener of the elbow button. It makes a ajax call for getting the elbow method plot.
 */
$("#elbow-button").on('click', function(){

    // generate spinner
    $("#elbow-results")[0].innerHTML = "<div class='spinner-border' role='status'></div>"

    // Ajax POST request that runs the elbow's method algorithm
    $.ajax({
        url: window.location.origin + '/ajax/run_elbow_method',
        cache:'false',
        dataType: 'json',
        type:"POST",
        data: {},
        headers:{
            "X-CSRFToken": csrftoken
        },
        async: true,
        success: function(data){

            // if the function successes, insert the image in the html code
            if (data.success){
                $("#elbow-results")[0].innerHTML = "<img src='data:image/png;base64," + 
                data["image"] + "' border='0' class='responsive-image' alt=''>";
            }
            else{
                alert("error: data didn't success");
            }
            
        },
        error: function(){
            alert('error; ');
        }
    });

});

/**
 * Function that handles the event listener of the run algorithm button. It makes a ajax call for running the algorithm and gets its results.
 */
$("#run-algorithm-button").on('click', function(){

    // Runs only if the selected algorithm is implemented
    if ($('#algorithm_menu').val() != "Kprototypes" && $('#algorithm_menu').val() != "KmeansDistributed"){
        window.alert("Este algoritmo no está aún implementado.");
    }

    else{

        // generate spinner
        $("#algorithm-results")[0].innerHTML = "<div class='spinner-border' role='status'></div>";

        // call the function that will store the algorithm parameters from the html form (two dictionaries null/not null values)
        algorithm_param = generateAlgorithmParamDict();

        // transform the boolean parameter so Python can perform a correct interpretation
        algorithm_parameters_string = JSON.stringify(algorithm_param["algorithm_parameters"]);
        algorithm_parameters_string = algorithm_parameters_string.replace(':true', ':True')
        algorithm_parameters_string = algorithm_parameters_string.replace(':false', ':False')

        // Ajax POST request that runs the selected algorithm
        $.ajax({
            url: window.location.origin + '/ajax/run_algorithm',
            cache:'false',
            dataType: 'json',
            type:"POST",
            data: {"algorithm_parameters":algorithm_parameters_string,
             "null_parameters":JSON.stringify(algorithm_param["null_parameters"]), "algorithm_name":$('#algorithm_menu').val()},
            headers:{
                "X-CSRFToken": csrftoken
            },
            async: true,
            success: function(data){

                // if the function successes, add all the results to the html view
                if (data.success){

                    // check if there has been an error in the dataset building
                    if ("info_user" in data){
                        alert(data["info_user"]);
                        $("#algorithm-results")[0].innerHTML = "";
                    }
                    else{

                        if ($('#algorithm_menu').val() == "Kprototypes"){
                            createKPrototypesHTMLResults(data);
                        }
                        else if($('#algorithm_menu').val() == "KmeansDistributed"){
                            createKMeansDistributedHTMLResults(data);
                        }

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

});

/**
 * Function that gets the parameters values from the view and stores them in a dictionary
 */
function generateAlgorithmParamDict(){

    // set an empty dictionary that will store the algorithm parameters from the html form (non null and null params)
    algorithm_parameters = {};
    null_parameters = {};

    // iterate all over the html form's elements
    for (i = 0; i<$("#algorithm_parameters")[0].children[0].length; i++){

        current_param = $("#algorithm_parameters")[0].children[0].children[i]

        // store in the dictionary the information about the current parameter, which is an integer or float. It gets it from the form
        if (current_param.classList[1].substring(3) == "Integer" || current_param.classList[1].substring(3) == "Float"){

            // if the parameter is numeric and the value an empty string, add it to null parameters dictionary
            if (current_param.children[1].value != ''){
                algorithm_parameters[current_param.children[0].innerText] = parseFloat(current_param.children[1].value)  
            }
            else{
                null_parameters[current_param.children[0].innerText] = "None"
            }
            
        }
        // store in the dictionary the information about the current parameter, which is a choice. It gets it from the form
        else if (current_param.classList[1].substring(3) == "Choice"){
            algorithm_parameters[current_param.children[0].innerText] = current_param.children[1].options[
                                                                    current_param.children[1].selectedIndex].value
        }
        // store in the dictionary the information about the current parameter, which is a boolean. It gets it from the form
        else if (current_param.classList[1].substring(3) == "Boolean"){
            algorithm_parameters[current_param.children[0].innerText] = current_param.children[0].children[0].checked
        }
        // store in the dictionary the information about the current parameter, which is a String. It gets it from the form
        else if (current_param.classList[1].substring(3) == "String"){
            algorithm_parameters[current_param.children[0].innerText] = String(current_param.children[1].value)
        }

    }

    return {"algorithm_parameters":algorithm_parameters, "null_parameters":null_parameters}
}

function createKPrototypesHTMLResults(data){

    // cluster centroids
    html_string = "<br><h5><b>Centroides normalizados</b> de los clusters</h5><table border='1' >";

    // table header
    html_string += "<tr>";
    for (i = 0; i < data["results_app"]["centroids_table_header"].length; i++){
        html_string += "<th>" + data["results_app"]["centroids_table_header"][i] + "</th>";
    }
    html_string += "</tr>";

    // table body
    for (i = 0; i < data["results_app"]["cluster_centroids"].length; i++){
        html_string += "<tr>";
        
        for (j = 0; j < data["results_app"]["cluster_centroids"][i].length; j++){
            html_string += "<td>" + data["results_app"]["cluster_centroids"][i][j] + "</td>";
        }
            
        html_string += "</tr>";
    }
    html_string += "</table>";

    // denormalized cluster centroids
    html_string += "<br><h5><b>Centroides desnormalizados</b> de los clusters</h5><table border='1'>";

    // table header
    html_string += "<tr>";
    for (i = 0; i < data["results_app"]["centroids_table_header"].length; i++){
        html_string += "<th>" + data["results_app"]["centroids_table_header"][i] + "</th>";
    }
    html_string += "</tr>";

    // table body
    for (i = 0; i < data["results_app"]["denormalized_centroids"].length; i++){
        html_string += "<tr>";
        
        for (j = 0; j < data["results_app"]["denormalized_centroids"][i].length; j++){
            html_string += "<td>" + data["results_app"]["denormalized_centroids"][i][j] + "</td>";
        }
            
        html_string += "</tr>";
    }
    html_string += "</table>";

    // number of iterations
    html_string += "<br><h5><b>Número de iteraciones</b> del algoritmo: " +  String(data["results_app"]["n_iter"]) + "</h5><br>";

    // cost of clusters
    html_string += "<h5><b>Coste</b> asociado a los clusters: " +  String(data["results_app"]["cost"]) + "</h5><br>";

    // rows of dataset
    html_string += "<h5>Primeras 5 <b>filas del dataset</b> con las etiquetas de los clústeres: </h5>" + 
                    data["results_app"]["dataset_w_cluster_labels"] + "<br/>";

    // results interpretation
    html_string += "<br><h5><b>Interpretación</b> de los resultados normalizados:</h5> " +
                    data["results_app"]["normalized_cluster_interpretation"] + "<br/>";

    // denormalized results interpretation
    html_string += "<br><h5><b>Interpretación</b> de los resultados desnormalizados:</h5> " +
                    data["results_app"]["denormalized_cluster_interpretation"] + "<br/>";

    // images/plots
    html_string += "<br><h5><b>Gráficos y resumen</b> de los resultados del algoritmo de los resultados desnormalizados:<h5><br>"
                    + "<img src='data:image/png;base64," + data["num_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>" 
                    + "<img src='data:image/png;base64," + data["cat_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>" 
                    + "<img src='data:image/png;base64," + data["cat_num_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>";

    // show the html
    $("#algorithm-results")[0].innerHTML = html_string;

}

function createKMeansDistributedHTMLResults(data){

    // cluster centroids
    html_string = "<br><h5><b>Centroides normalizados</b> de los clusters</h5><table border='1' >";

    // table header
    html_string += "<tr>";
    for (i = 0; i < data["results_app"]["centroids_table_header"].length; i++){
        html_string += "<th>" + data["results_app"]["centroids_table_header"][i] + "</th>";
    }
    html_string += "</tr>";

    // table body
    for (i = 0; i < data["results_app"]["cluster_centroids"].length; i++){
        html_string += "<tr>";
        
        for (j = 0; j < data["results_app"]["cluster_centroids"][i].length; j++){
            html_string += "<td>" + data["results_app"]["cluster_centroids"][i][j] + "</td>";
        }
            
        html_string += "</tr>";
    }
    html_string += "</table>";

    // denormalized cluster centroids
    html_string += "<br><h5><b>Centroides desnormalizados</b> de los clusters</h5><table border='1'>";

    // table header
    html_string += "<tr>";
    for (i = 0; i < data["results_app"]["centroids_table_header"].length; i++){
        html_string += "<th>" + data["results_app"]["centroids_table_header"][i] + "</th>";
    }
    html_string += "</tr>";

    // table body
    for (i = 0; i < data["results_app"]["denormalized_centroids"].length; i++){
        html_string += "<tr>";
        
        for (j = 0; j < data["results_app"]["denormalized_centroids"][i].length; j++){
            html_string += "<td>" + data["results_app"]["denormalized_centroids"][i][j] + "</td>";
        }
            
        html_string += "</tr>";
    }
    html_string += "</table>";

    // number of iterations
    html_string += "<br><h5><b>Coeficiente de silueta (silhouette): " +  String(data["results_app"]["silhouette"]) + "</h5><br>";

    // rows of dataset
    html_string += "<h5>Primeras 5 <b>filas del dataset</b> con las etiquetas de los clústeres: </h5>" + 
                    data["results_app"]["dataset_w_cluster_labels"] + "<br/>";

    // results interpretation
    html_string += "<br><h5><b>Interpretación</b> de los resultados normalizados:</h5> " +
                    data["results_app"]["normalized_cluster_interpretation"] + "<br/>";

    // denormalized results interpretation
    html_string += "<br><h5><b>Interpretación</b> de los resultados desnormalizados:</h5> " +
                    data["results_app"]["denormalized_cluster_interpretation"] + "<br/>";

    // images/plots
    html_string += "<br><h5><b>Gráficos y resumen</b> de los resultados del algoritmo de los resultados desnormalizados:<h5><br>"
                    + "<img src='data:image/png;base64," + data["num_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>" 
                    + "<img src='data:image/png;base64," + data["cat_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>" 
                    + "<img src='data:image/png;base64," + data["cat_num_image"] + "' border='0' class='responsive-image' alt='' "
                    + "width='1000' <br/><br/>";

    // show the html
    $("#algorithm-results")[0].innerHTML = html_string;

}

/**
 * Function that handles the event listener of the elbow button. It makes a ajax call for getting the elbow method plot.
 */
function refreshElbowMethodListener(algorithmParametersInfo){

    // remove the code
    $("#elbow-method").empty()

    // turn off the previous listener
    $('.elbow-button').off(); 

    if ($('#algorithm_menu').val() == "Kprototypes"){

        debugger;

        // add the code in case the selected algorithm is KPrototypes
        content_html = "<h5>Ayuda con la selección del número de clústeres empleando la técnica <b>Elbow's Method</b></h5>"
        + "<button type='button' class='btn btn-primary btn-lg' id='elbow-button'>Ejecutar Elbow's Method</button>"
        + "<div id='elbow-results'></div></br></br>"

        $("#elbow-method")[0].innerHTML = content_html
        
        // turn on the new listener
        $("#elbow-button").on('click', function(){

            // generate spinner
            $("#elbow-results")[0].innerHTML = "<div class='spinner-border' role='status'></div>"

            // Ajax POST request that runs the elbow's method algorithm
            $.ajax({
                url: window.location.origin + '/ajax/run_elbow_method',
                cache:'false',
                dataType: 'json',
                type:"POST",
                data: {},
                headers:{
                    "X-CSRFToken": csrftoken
                },
                async: true,
                success: function(data){

                    // if the function successes, insert the image in the html code
                    if (data.success){
                        $("#elbow-results")[0].innerHTML = "<img src='data:image/png;base64," + 
                        data["image"] + "' border='0' class='responsive-image' alt=''>";
                    }
                    else{
                        alert("error: data didn't success");
                    }
                    
                },
                error: function(){
                    alert('error; ');
                }
            });

        });

    }

    

}