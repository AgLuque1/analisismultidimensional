//función que obtiene las columnas de una experimentación seleccionada
var metadatos = [];
var filas = [];

function obtenerColumnas(){

    var experimentacionSeleccionada = $("#experimentaciones").val();

    if(experimentacionSeleccionada != ''){

        //Extraemos el nombre del experimento, ya que el experimento tiene el formato fecha/nombre
        //Usamos una expresión regular para extraer el nombre
        var nombre = experimentacionSeleccionada.match(/\/\s*([^\/]+)/)[1];

        //Realizamos petición ajax
        $.ajax({
                url: "/analisismultidimensional/obtener-columnas",  //Reemplazamos con la URL de la vista en Django
                data: {'nombre_experimentacion': nombre},
                dataType: 'json',
                success: function(data) {
                    //Limpiamos las opciones actuales
                    $("#columnas").empty();
    
                    //Llenamos las opciones del segundo select con las columnas del experimento
                    $.each(data.columnas, function(index, columna) {
                        var metadatosColumna = metadatos.find(obj => obj.Code === columna);


                        $("#columnas").append('<option value="' + columna + '">' + columna + ' - ' + metadatosColumna.VarType  +'</option>');
                    });
                }
            });
    }
}



//Función que obtiene las experimentaciones asociadas la bd
function obtenerExperimentaciones(){

    var bdSeleccionada = $("#basesdedatos").val().replace(/\s/g, '');
    console.log("La base de datos es: " + bdSeleccionada);

    //Realizamos petición para que devuelva los experimentos asociados a dicha BD
    $.ajax({
        url: "/analisismultidimensional/obtener-experimentaciones",
        data: {'nombre_bd': bdSeleccionada},
        dataType: 'json',
        success: function(data){

            //Limpiamos las experimentaciones actuales
            $("#experimentaciones").empty();

            $("#experimentaciones").append('<option value="' + '' + '">' + '' + '</option>');
            //Creamos una opción por cada experimentación y la añadimos al select
            $.each(data.experimentaciones, function(index, experimentacion) {
                $("#experimentaciones").append('<option value="' + experimentacion + '">' + experimentacion + '</option>');
            });

        }
    });

    //Realizamos una petición para los metadatos de las  variables de la base de datos seleccionada
    $.ajax({
        url: "/analisismultidimensional/obtener-meta",
        data: {'nombre_bd': bdSeleccionada},
        dataType: 'json',
        success: function(data){
           
            metadatos = data.metadatos;
            $('#experimentaciones').prop('disabled', false);
            $('#columnas').prop('disabled', false);
            
        }
    });
}

function obtenerFilas(){
    
    var bdSeleccionada = $("#basesdedatos").val().replace(/\s/g, '');

    //Realizamos otra petición para obtener las filas de la base de datos, con las que se creará el cubo
    $.ajax({
        url: "/analisismultidimensional/obtener-filas",
        data: {'nombre_bd': bdSeleccionada},
        dataType: 'json',
        success: function(data){
           
            filas = data.filas;
            console.log("PETICION DE FILAS FINALIZADA. IMPRIMIENDO");
            console.log(filas);
            
        }
    });
    
}
