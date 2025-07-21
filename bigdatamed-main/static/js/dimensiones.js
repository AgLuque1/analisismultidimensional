// Funciones para la gestión de creación de dimensiones, jerarquías y niveles

//Variable donde almacenamos el cubo completo
var cubo = {}



var estructuraCubo = {};
estructuraCubo.dimensiones = {};

//Variable donde almacenamos nombre del cubo
var nombreCubo;

//Variable donde almacenamos referencia de la experimentación de la que procede
var nombreExperimentacion;

//Variable donde almacenamos la descripción del cubo
var descripcion;

//Variable donde almacenamos el usuario actual
var user;

//Variable donde almacenamos la fecha de creación del cubo
var date;
var dia = new Date().getDate();
var mes = new Date().getMonth() +1;
var ano = new Date().getFullYear();

if(dia < 10){
  dia = "0" + dia;
}

if(mes < 10){
  mes = "0" + mes;
}

date = dia + "/" + mes + "/" + ano;

//Variable donde almacenamos el nombre de la medida
var nombreMedida;

//Variable donde almacenamos la medida escogida
var medida;

//Variable donde almacenamos el tipo de medida
var tipoMedida;

//Variable que representa la estructura del cubo en forma de árbol
var tree = $('#tree');

//Inicializamos los select
$(document).ready(function(){

  añadirJerarquiaPorDefecto();
  
  user = document.getElementById('usuario').getAttribute('data-usuario');
  
  $('#dimensiones').select2({
    minimumResultsForSearch: Infinity
  });

  $('#basesdedatos').select2({
    minimumResultsForSearch: Infinity
  });

  $('#experimentaciones').select2({
    minimumResultsForSearch: Infinity
  });


  $('#dimensionesJerarquias').select2({
    minimumResultsForSearch: Infinity,
    
  });
  
  $('#niveles').select2({
    minimumResultsForSearch: Infinity,
  });

  $('#columnasSeleccionadas').select2({
    minimumResultsForSearch: Infinity,
  });

  $('#medidas').select2({
    minimumResultsForSearch: Infinity,
  });
  


  //EVENTOS DE BORRADO
  const borrarDimension = document.getElementById("borrarDimension");
  const borrarJerarquia = document.getElementById("borrarJerarquia");
  const borrarNivel = document.getElementById("borrarNivel");


  borrarDimension.addEventListener("click", () => {
    
    //Comprobamos que haya una dimensión seleccionada
    var dimension = document.getElementById('dimensiones').value;

    if(dimension === ''){
      if(language === 'es')
        toastr.error('No hay dimensiones seleccionadas');
      else
        toastr.error('No dimensions selected');
      return;
    }
    else{
      
      //Llamamos al modal
      $('#modalDimension').modal('show')

    }
  });

  borrarJerarquia.addEventListener("click", () => {
    
    //Comprobamos que haya una jerarquia seleccionada
    var jerarquia = $('#dimensionesJerarquias').val();
   
    if(jerarquia === null || jerarquia === ''){
      if(language === 'es')
        toastr.error('No hay jerarquía seleccionada');
      else
      toastr.error('No hierarchies selected');
      return;
    }
    else{
      
      //Llamamos al modal
      $('#modalJerarquia').modal('show')

    }
  });

  borrarNivel.addEventListener("click", () => {
    
    //Comprobamos que haya una jerarquia seleccionada
    var nivel = $('#niveles').val();

    if(nivel === '' || nivel === null){
      if(language === 'es')
        toastr.error('No hay niveles seleccionados');
      else
      toastr.error('No levels selected');
      return;
    }
    else{
      
      //Llamamos al modal
      $('#modalNivel').modal('show')

    }
  });
  

  //Inicializamos Fancytree
  tree.fancytree({
    source: [],
    nodata: false,
    click: function(event, data) {
    },
  });

  tree = $.ui.fancytree.getTree("#tree");

  //Validación de los inputs para que no se introduzcan caracteres no deseados
  const inputs = document.querySelectorAll('.input-validar');

  inputs.forEach(input => {
    input.addEventListener('input', function(event) {

      const valorInput = event.target.value;

      //Verificamos si el valor contiene comas, puntos u otros caracteres no deseados
      if (valorInput.match(/[,:;¿?~.¡!@#$%^&*'`()_+=<>?{}|[\]\\/]/)) {

        //Si se encuentra algún carácter no deseado, se limpia el valor del campo de entrada
        event.target.value = valorInput.replace(/[,:;¿?.~¡!@#$%^&*()_+`'=<>?{}|[\]\\/]/g, '');
        if(language === 'es')
          toastr.error("Introduce caracteres válidos");
        else
          toastr.error("Enter valid characters");
      }

    });
  });

});

//Gestiona los disableds
// Habilita o deshabilita el botón según el cambio en el select2
  $('#niveles').on('change', function() {
    $('#botonCrearDimension').prop('disabled', $(this).val() === null);
  });

  $('#dimensiones').on('change', function() {
    $('#botonCrearJerarquia').prop('disabled', $(this).val() === null);
    $('#borrarDatos').prop('disabled', $(this).val() === null);
  });

  $('#dimensionesJerarquias').on('change', function() {
    $('#botonCrearNivel').prop('disabled', $(this).val() === null);
  });

  $('#tree').on('change', function() {
    $('#botonCrearMedida').prop('disabled', $(this).val() === null);
  });

  
  $('#medidas').on('change', function() {
    $('#botonTerminar').prop('disabled', $(this).val() === null);
  });
  


 //Función que agrega dimensiones al select para poder crear jerarquías
function agregarDimension() {

   //Obtenemos el valor del input
   var dimension = document.getElementById('nombreDimension').value;

   //Si la dimensión no está vacía y no existe, la añadimos al select
   if (dimension.trim() !== '' && !estructuraCubo.dimensiones.hasOwnProperty(dimension)) {
    
     estructuraCubo.dimensiones[dimension] = {};
     
     estructuraCubo.dimensiones[dimension]['jerarquias'] = {};
   
     if(language === 'es')
      toastr.success('Dimensión añadida');
     else
     toastr.success('Dimension added');

     //Limpiamos el input después de agregar la opción
     document.getElementById('nombreDimension').value = '';

     //Actualizamos los cambios en el select
     actualizarJerarquias();

     $('#dimensiones').val(null).trigger('change.select2');

     actualizarArbol();
     actualizarDimensiones();
     imprimirArbol();

     console.log(estructuraCubo);

     //Si la dimensión existe, informa error
   } else if (estructuraCubo.dimensiones.hasOwnProperty(dimension)){
     if(language === 'es')
      toastr.error('Ya existe una dimensión con ese nombre');
     else
      toastr.error('There is already a dimension with that name');
   }
   else{
     if(language === 'es')
      toastr.error('Introduce un nombre de dimensión');
     else
      toastr.error('Enter a dimension name');
   }

   

 }


//Funcion que añade jerarquia a una dimensión
function añadirJerarquia(){

    //Obtenemos nombre de la dimensión seleccionada y la jerarquía
    var nombreJerarquia = $('#nombreJerarquia').val();
    var dimensionSeleccionada = $('#dimensiones').val();
   
    //Comprobamos si se ha introducido nombre de jerarquía y hay una dimensión seleccionada
    if(nombreJerarquia.trim() !== '' && dimensionSeleccionada !== null){

        //Comprobamos si la jerarquía ya existe
        console.log("Comprobando si la jerarquia ya existe");
        if(!estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias
        .hasOwnProperty(nombreJerarquia)){
            estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias[nombreJerarquia] = {};
            
            if(language === 'es')
              toastr.success('Jerarquia añadida');
            else
            toastr.success('Hierarchy added');
        } else{
            if(language === 'es')
              toastr.error('Ya existe una jerarquía con ese nombre');
            else
              toastr.error('There is already a hierarchy with that name');
            return;
        }
        
    
        //Limpiamos el input después de añadir la jearquía
        $('#nombreJerarquia').val('');
    
        
        //Actualizamos los cambios en el select
        actualizarJerarquias();
        $('#dimensiones').val(null).trigger('change.select2');
        $('#dimensionesJerarquias').val(null).trigger('change.select2');

        actualizarArbol();
        imprimirArbol();
        console.log(estructuraCubo);
        añadirJerarquiaPorDefecto();
        actualizarEstructuraCubo();
    }
    else {
      if (language ==='es')
        toastr.error('Introduce un nombre de jerarquía y selecciona una dimensión');
      else
        toastr.error('Enter a hierarchy name and select a dimension');
    }
 }

 
//Función que añade un nivel a una jerarquía
function añadirNivel(){

  var nombreNivel = $('#nombreNivel').val();

  var nombreJerarquia = $('#dimensionesJerarquias').val();
  
  var nivelSeleccionado = $('#niveles').val();

  //Comprobar que se han seleccionado dimension y jerarquia
  if (nombreJerarquia.trim() === ''){
    if(language === 'es')
      toastr.error("Selecciona una jerarquía");
    else
      toastr.error("Select a hierarchy");
  }

  if(nivelSeleccionado === null){
  return;
  }

  //Si no se ha dado nombre de nivel, le asignamos el de la columna
  if(nombreNivel.trim() ===''){
    nombreNivel = nivelSeleccionado;
  }

  //Comprobamos si el nivel ya se ha añadido
  console.log("Comprobando si el nivel está añadido");
  var encontrado = false;
  
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia){
      if(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].hasOwnProperty(nivelSeleccionado)) {
        encontrado = true;
        if(language === 'es')
          toastr.error("El nivel ya se ha añadido");
        else  
          toastr.error("The level has already been added");
      }
    });
  });

  if (!encontrado){

    var nombreDimension;
        
    //Buscamos el nombre de la dimensión a la que pertenece la jerarquía
    Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
      if (estructuraCubo.dimensiones[dimension].jerarquias.hasOwnProperty(nombreJerarquia)) {
          nombreDimension = dimension;
          return;
      }
    });

    //Añadimos el nivel
  
    estructuraCubo.dimensiones[nombreDimension].jerarquias[nombreJerarquia][nivelSeleccionado] = nombreNivel;
    if(language === 'es')
      toastr.success('Nivel añadido');
    else
      toastr.success('Level added');
    
    $('#niveles').val('');

    //Limpiamos el input después de añadir la jearquía
    $('#nombreNivel').val('');

    $('#niveles').val(null).trigger('change.select2');
    //Acutlizamos los cambios en el arbol
    actualizarSelectMedidas(nivelSeleccionado, 'añadir');
    console.log(estructuraCubo);
    actualizarArbol();
    imprimirArbol();
    
  } 
}

function añadirJerarquiaPorDefecto(){

  
  $('#contenedorDimensiones').empty();

  var titulo = $('<h5 style="font-weight="bold"">' + "Seleccionar jerarquías por defecto" + '</h5>');
  $('#contenedorDimensiones').append(titulo);
  

  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    

    var label = $('<label>' + dimension + '</label>' + '<br>');
    
    var select = $('<select class="form-control select2" id="jerarquiadefecto_' + dimension + '"></select>' + '<br>');
    var jerarquias = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias);

    var dimensionContenedor = $('<div class="dimension-container"></div>');
;
    //Iteramos sobre las jerarquías y las añadimos al select
    jerarquias.forEach(function(jerarquia) {
      var option = $('<option value="' + jerarquia + '">' + jerarquia +  '</option>');
      select.append(option);
    });


    //Creamos una lista ordenable, para que se puedan arrastrar las opciones
    var lista = $('<ul class="lista-ordenable" id="ordenable_' + dimension + '"></ul>');
    jerarquias.forEach(function(jerarquia) {
      var item = $('<li id="' + jerarquia  + '">' + jerarquia + '</li>');
      lista.append(item);
    });

    dimensionContenedor.append(label);
    dimensionContenedor.append(select);
    dimensionContenedor.append('<label>Arrastra para establecer el orden de Jerarquías (más general a más específica)</label>');
    dimensionContenedor.append(lista)
    $('#contenedorDimensiones').append(dimensionContenedor)

    /*
    select.select2({
      minimumResultsForSearch: Infinity
    });*/
  
    $('#jerarquiadefecto_' + dimension).select2({
      minimumResultsForSearch: Infinity,
      
    });

    $('#jerarquiadefecto_' + dimension).on('change', function() {
      console.log("Esta cambiando");
      actualizarEstructuraCubo();
      actualizarArbol();
    });
    /*
    $('#jerarquiadefecto_' + dimension).on('change',function() {
      console.log("Esta cambiando");
      actualizarEstructuraCubo();
      actualizarArbol();
    })*/

    $('#ordenable_' + dimension).sortable();
    $('#ordenable_' + dimension).disableSelection();
  });

 

}

function actualizarEstructuraCubo(){
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension){
    var jerarquiaPorDefecto = $('#jerarquiadefecto_' + dimension).val();
    console.log("Jerarquia por defecto de la dimension: " + dimension + " es: " + jerarquiaPorDefecto);
    estructuraCubo.dimensiones[dimension].jerarquia_por_defecto = jerarquiaPorDefecto;

    var listajerarquias = [];
    $('#ordenable_' + dimension).children('li').each(function() {
      console.log("Añadiendo id a la lista de jerarquias");
      listajerarquias.push(this.id)
    });
 

    //Borramos las jerarquias existenes
    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {
      delete estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_general;
      delete estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_especifica;   
    });

    console.log("Jerarquias tiene longitud: " + listajerarquias.length);
    
    for(var i=0; i< listajerarquias.length; i++){
      var jerarquia = listajerarquias[i];
      if(i > 0) {
        estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_general = listajerarquias[i-1];
      }
      else {
        estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_general = null;
      }
      if ( i < listajerarquias.length -1 ){
        estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_especifica = listajerarquias[i+1];
      }
      else {
        estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].mas_especifica = null;
      }
    }

  });

  actualizarArbol();

  console.log("Cubo final");
  console.log(JSON.stringify(estructuraCubo, null, 2));

}
//Función que actualiza el select de dimensiones
function actualizarDimensiones(){

  //Limpiamos el select
  $('#dimensiones').empty();

  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    var option = $('<option value="' + dimension + '">' + dimension +  '</option>');

    //Añadimos la opcion al select
    $('#dimensiones').append(option);
  });

  $('#dimensiones').val(null).trigger('change.select2');

}

//Función que actualiza el select de jerarquías
function actualizarJerarquias() {

  //Limpiamos el select
  $('#dimensionesJerarquias').empty();

  //Iteramos sobre las dimensiones y agregamos los optgroups y las jerarquias
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    var optgroup = $('<optgroup label="' + dimension + '"></optgroup>');

    var jerarquias = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias);

    //Iteramos sobre las jerarquías y las añadimos a la dimensión
    jerarquias.forEach(function(jerarquia) {
      var option = $('<option value="' + jerarquia + '">' + jerarquia +  '</option>');
      optgroup.append(option);
    });

    //Añadimos el optgroup al select
    $('#dimensionesJerarquias').append(optgroup);
  });

  //Actualizamos el segundo select y el select final
  $('#dimensionesJerarquias').val(null).trigger('change.select2');

}


//Función que elimina dimensión
function eliminarDimension(){
  
  //Recuperamos la dimension seleccionada para borrar
  var dimension = document.getElementById('dimensiones').value;

  //Comprobamos que la dimensión existe en el estructura
  if(estructuraCubo.dimensiones.hasOwnProperty(dimension)){
    
    //Eliminamos la dimensión
    delete estructuraCubo.dimensiones[dimension];
    if(language === 'es')
     toastr.success("Dimensión eliminada");
    else
      toastr.success("Dimension removed");


    //Eliminamos la dimensión del select
    $("#dimensiones").find('option[value="' + dimension + '"]').remove();
    $('#dimensiones').val(null).trigger('change.select2');

    //Ocultamos el modal
    $('#modalDimension').modal('hide')

    //Actualizamos el arbol
    actualizarArbol();
    actualizarDimensiones();
    actualizarJerarquias();
    imprimirArbol();

  }
}

//Función que elimina dimensión
function eliminarJerarquia(){
  
  //Recuperamos la jerarquía seleccionada para borrar
  var jerarquia = $('#dimensionesJerarquias').val();

  //Comprobamos que la jerarquía existe en el estructura, si existe la borra
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
  if(estructuraCubo.dimensiones[dimension].jerarquias.hasOwnProperty(jerarquia)){
    delete estructuraCubo.dimensiones[dimension].jerarquias[jerarquia];
    return;
  }

  });

  if(language === 'es')
    toastr.success("Jerarquía eliminada");
  else
    toastr.success("Hierachy removed");

  //Ocultamos el modal
  $('#modalJerarquia').modal('hide');

  //Actualizamos el arbol
  actualizarArbol();
  imprimirArbol();

  //Actualizamos el select de jerarquias
  actualizarJerarquias();
  añadirJerarquiaPorDefecto();
  actualizarEstructuraCubo();

  
}

//Función que elimina nivel
function eliminarNivel(){
  
  //Recuperamos la jerarquía seleccionada para borrar
  var nivel = $('#niveles').val();


  //Ocultamos el modal
  $('#modalNivel').modal('hide');

  //Comprobamos que el nivel existe en el estructura, si existe lo borra
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {

      if(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].hasOwnProperty(nivel)) {

        delete estructuraCubo.dimensiones[dimension].jerarquias[jerarquia][nivel];
        if(language === 'es')
          toastr.success("Nivel eliminado");
        else
        toastr.success("Level removed");
        actualizarSelectMedidas(nivel, 'eliminar');
      }
      else{
        if(language === 'es')
          toastr.error("El nivel no pertenece al cubo");
        else
        toastr.error("The level does not belong to the cube");
      }
    });
  });

  
  //Actualizamos el select de medidas
  
  //Actualizamos el arbol
  actualizarArbol();
  imprimirArbol();

}

function actualizarSelectMedidas(nivel, opcion){

  //Si añadimos un nivel al cubo, no lo podemos utilizar como medida, por lo que lo deshabilitamos de las medidas
  if(opcion === 'añadir'){
    var $option = $('#columnasSeleccionadas').find('option:contains("' + nivel + '")');

    if($option.length){
      $option.remove();
    }

    $('#columnasSeleccionadas').val(null).trigger('change.select2');
  }

  //Si eliminamos el nivel del cubo, vuelve a estar disponible para añadirlo como medida
  else if(opcion === 'eliminar'){
    $('#columnasSeleccionadas').append('<option value="' + nivel + '">' + nivel + '</option>');
    $('#columnasSeleccionadas').val(null).trigger('change.select2');
  }
}

function actualizarArbol(){

  //Borramos el árbol actual
  var tree = $.ui.fancytree.getTree("#tree");
  tree.getRootNode().removeChildren();
  
  //Iteramos por las dimensiones
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    console.log("Dentro de la dimension: " + dimension);
    // Creamos nodo para la dimensión
    tree.getRootNode().addChildren({
    title: dimension,
    extraClasses: "fancytree-dimension ",
    icon: "icono-dimension",
    // Otras opciones de nodo
    });

    tree.expandAll();  

    // Iteramos sobre las jerarquías de la dimensión
    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {

        console.log("Dentro de la jerarquia: " + jerarquia);
        // Creamos nodo para la jerarquía
        var nodoDimension = tree.findFirst(dimension);
      
        if(nodoDimension){
          if(estructuraCubo.dimensiones[dimension].jerarquia_por_defecto == jerarquia){
            nodoDimension.addChildren({
              title: jerarquia,
              extraClasses: "fancytree-jerarquia-defecto",
              icon: "icono-jerarquia",
            });
          }
          else {
            nodoDimension.addChildren({
              title: jerarquia,
              extraClasses: "fancytree-jerarquia",
              icon: "icono-jerarquia",
            });
          }
          tree.expandAll();
        }

        // Iteramos sobre los niveles de la jerarquia
        var niveles = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia]);
        
        console.log("Dentro de los niveles");

        niveles.forEach(function(nivel) {

          console.log("Procesando nivel: " + nivel);

            if(nivel == 'mas_general' || nivel == 'mas_especifica'){
              return;
            }
            else{
              // Creamos nodo para el nivel
              var nodoJerarquia = tree.findFirst(jerarquia);

              if(nodoJerarquia){
                nodoJerarquia.addChildren({
                  title: estructuraCubo.dimensiones[dimension].jerarquias[jerarquia][nivel] + ' - ' + nivel,
                  extraClasses: "fancytree-nivel",
                  icon: "icono-nivel",
                });
                tree.expandAll();
              }
           }
             
        });
    });
});

}

function imprimirArbol(){

  console.log(nombreCubo);
  console.log("Imprimiendo árbol");

  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    console.log("Dimensión: " + dimension)
    // Iteramos sobre las jerarquías de la dimensión
    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {

        console.log("Jerarquia: " + jerarquia);
        // Iteramos sobre los niveles de la jerarquia
        var niveles = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia]);

        niveles.forEach(function(nivel) {

          console.log("Nivel: " + nivel);
            
        });
    });

  });

  console.log("Arbol acabado");

  console.log(estructuraCubo.dimensiones);
}

//Función que comprueba que no haya jerarquías vacías antes de guardar el cubo
function comprobarJerarquiasVacias(){

  //Iteramos sobre cada dimensión
  for (var dimension in estructuraCubo.dimensiones) {

    //Comprobamos si la dimensión tiene jerarquías
    if (Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).length === 0) {
      if(language === 'es')
        toastr.error("Dimensión: " + dimension + " sin completar");
      else
        toastr.error("Dimension: " + dimension + " not completed");
      return true;
    }
    else {

      //Iteramos sobre cada jerarquía
      for (var jerarquia in estructuraCubo.dimensiones[dimension].jerarquias) {

        //Comprobamos si la jerarquía tiene al menos un nivel
        if (Object.keys(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia]).length === 0) {
            if(language === 'es')
              toastr.error("Jerarquía: " + jerarquia + " sin completar");
            else
              toastr.error("Hierarchy: " + jerarquia + " not completed");
            return true;
        }
      } 
    }   
  } 

  //Si todas las jerarquías tienen al menos un nivel, devolvemos false
  return false;
}

function enviarCubo(){

  actualizarEstructuraCubo();

  var vacias = comprobarJerarquiasVacias();
  console.log(vacias);

  nombreCubo = $('#cubename').val();
  nombreExperimentacion = $("#experimentaciones").val()
  nombreExperimentacion = nombreExperimentacion.match(/\/\s*([^\/]+)/)[1];
  descripcion = $('#description').val();
  nombreMedida = $('#nombreMedida').val();
  medida = $('#columnasSeleccionadas').val();
  tipoMedida = $('#medidas').val();

  console.log("IMPRIMIENDO VALORES FINALES");
  console.log("Nombre cubo: " + nombreCubo);
  console.log("nombre experimentacion: " + nombreExperimentacion);
  console.log("medida: " + medida);
  console.log("tipo medida: " + tipoMedida);
  console.log("Estructura: ");
  console.log(estructuraCubo.dimensiones);

  console.log("Haciendo OBJETO COMPLETO");

  cubo = {user, date, nombreCubo, descripcion, nombreExperimentacion, ...estructuraCubo, nombreMedida, medida, tipoMedida};

  console.log("Mostrando Cubo Final");
  console.log(cubo);

  // Obtenemos el token CSRF del documento HTML
  var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

  //Realizamos petición ajax
   
  cubo_json = JSON.stringify(cubo);
  console.log("Cubo en json");
  console.log(cubo_json);

  console.log("Enviando peticion POST");
  $.ajax({
    url: "/analisismultidimensional/crear-cubo",  //Reemplazamos con la URL de la vista en Django
    headers: {
      'X-CSRFToken': csrfToken
    },
    type: "POST",
    data: {'cubo': JSON.stringify(cubo)},
    dataType: 'json',
    success: function(data) {
      console.log(data)
      if(data.success){
        if(language === 'es')
          toastr.success("Cubo creado correctamente");
        else
          toastr.success("Cube created successfully");
      } else {
        if(language === 'es')
          toastr.error("Ya existe un cubo con ese nombre");
        else
          toastr.success("There is already a cube with that name");
      }
      
    }
  });

  }