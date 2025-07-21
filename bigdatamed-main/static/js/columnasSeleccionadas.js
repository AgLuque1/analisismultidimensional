//Función para añadir las columnas seleccionadas de la experimentación a los select de las medidas y de la estructura del cubo

$(document).ready(function() {
    //Inicializamos Select2 en los selects
    $('#columnas').select2();
    $('#columnasSeleccionadas').select2();
    $('#niveles').select2();
  
   //Capturamos cambios en el primer select
    $('#columnas').on('change', function() {

      //Obtenemos los valores seleccionados
      var colsSeleccionadas = $(this).val();
  
      //Limpiamos los otros select antes de agregar las nuevas columnas
      $('#columnasSeleccionadas').empty();
      $('#niveles').empty();
      
      //Iteramos sobre el array, añadiendo cada nueva columna

      colsSeleccionadas.forEach((columna) => {

        var metadatosColumna = metadatos.find(obj => obj.Code === columna);
        //var metadatosColumna = metadatos[0].Code;

        $('#niveles').append('<option value="' + columna + '">' + columna + ' - ' + metadatosColumna.VarType  + '</option>');

        if(metadatosColumna.VarType === 'Numerical'){
          $('#columnasSeleccionadas').append('<option value="' + columna + '">' + columna + ' - ' + metadatosColumna.VarType  + '</option>');
        }
        
      })

     
      $('#columnasSeleccionadas').trigger('change');
      $('#niveles').trigger('change');
    });
  });
  