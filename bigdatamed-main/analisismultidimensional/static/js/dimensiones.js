// Script con funciones para la gestión de creación de dimensiones, jerarquías y niveles

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

  inicializarTraducciones();
  console.log("Traducciones finaleizasds");
  
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
      var mensaje = i18next.t('errorDimensionSeleccionada');
      toastr.error(mensaje)
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
      var mensaje = i18next.t('errorJerarquiaSeleccionada');
      toastr.error(mensaje)
      return;
    }
    else{
      
      //Llamamos al modal
      $('#modalJerarquia').modal('show')
    }
  });

  borrarNivel.addEventListener("click", () => {
    
    //Comprobamos que haya un nivel seleccionado
    var nivel = $('#niveles').val();

    if(nivel === '' || nivel === null){
      var mensaje = i18next.t('errorNivelSeleccionado');
      toastr.error(mensaje)
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
      var nodo = data.node;
      // Obtener el tipo de nodo y su contenido
      var tipoNodo = nodo.data.tipo;
      var contenidoNodo = nodo.title;

      var match = contenidoNodo.match(/<span class="titulo-nivel">(.*?)<\/span>/);
      var valorNodo = "";
      if (match && match[1]){
        valorNodo = match[1];
      } else {
        
        valorNodo = nodo.title;
      }
      var valor = valorNodo || "";
      // Actualizar el contenido del span con la información del nodo activado
      $("#infonodo").text(i18next.t('tipoNodo', {tipo: tipoNodo}));
      $("#infovalor").text(i18next.t('nombreNodo', {valor: valor}));
    },
    renderTitle: function(event, data) {
        data.node.span.innerHTML = data.node.title;
      }
  });

  tree = $.ui.fancytree.getTree("#tree");

  //Validación de los inputs para que no se introduzcan caracteres no deseados
  const inputs = document.querySelectorAll('.input-validar');

  inputs.forEach(input => {
    input.addEventListener('input', function(event) {

      const valorInput = event.target.value;

      //Verificamos si el valor contiene comas, puntos u otros caracteres no deseados
      if (valorInput.match(/[,\s":;¿?~.¡!@#$%^&*'`()_+=<>?{}|[\]\\/]/)) {

        //Si se encuentra algún carácter no deseado, se limpia el valor del campo de entrada
        event.target.value = valorInput.replace(/[\s,:;"¿?.~¡!@#$%^&*()_+`'=<>?{}|[\]\\/]/g, '');
        var mensaje = i18next.t('errorCaracter');
        toastr.error(mensaje)
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
   var dimension = document.getElementById('nombreDimension').value.trim();

   //Si la dimensión no está vacía y no existe, la añadimos al select
   if (dimension.trim() !== '' && !estructuraCubo.dimensiones.hasOwnProperty(dimension)) {
    
     estructuraCubo.dimensiones[dimension] = {};
     
     estructuraCubo.dimensiones[dimension]['jerarquias'] = {};

     var mensaje = i18next.t('exitoCrearDimension')
     toastr.success(mensaje)
     
     //Limpiamos el input después de agregar la opción
     document.getElementById('nombreDimension').value = '';

     //Actualizamos los cambios en el select
     actualizarJerarquias();

     $('#dimensiones').val(null).trigger('change.select2');

     actualizarDimensiones();
     actualizarArbol();
     //imprimirArbol();

     //Si la dimensión existe, informa error
   } else if (estructuraCubo.dimensiones.hasOwnProperty(dimension)){
     var mensaje = i18next.t('yaExisteDim');
     toastr.error(mensaje);
   }
   else{
     var mensaje = i18next.t('introduceDim');
     toastr.error(mensaje);
   }

 }


//Funcion que añade jerarquia a una dimensión
function añadirJerarquia(){

    //Obtenemos nombre de la dimensión seleccionada y la jerarquía
    var nombreJerarquia = $('#nombreJerarquia').val().trim();
    var dimensionSeleccionada = $('#dimensiones').val().trim();
   
    //Comprobamos si se ha introducido nombre de jerarquía y hay una dimensión seleccionada
    if(nombreJerarquia.trim() !== '' && dimensionSeleccionada !== null){

        //Comprobamos si la jerarquía ya existe
        if(!estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias
        .hasOwnProperty(nombreJerarquia)){
            estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias[nombreJerarquia] = {};
            estructuraCubo.dimensiones[dimensionSeleccionada].jerarquia_por_defecto=nombreJerarquia;
            estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias[nombreJerarquia].niveles = [];
            estructuraCubo.dimensiones[dimensionSeleccionada].jerarquias[nombreJerarquia].nivel_actual = "";
            var mensaje = i18next.t('exitoCrearJerarquia');
            toastr.success(mensaje);
        } else{
            var mensaje = i18next.t('yaExisteJer');
            toastr.error(mensaje);
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
    }
    else {
      var mensaje = i18next.t('introduceJer');
      toastr.error(mensaje);
    }
 }

//Función que añade un nivel a una jerarquía
function añadirNivel(){

  var nombreNivel = $('#nombreNivel').val().trim();
  var nombreJerarquia = $('#dimensionesJerarquias').val().trim();
  var nivelSeleccionado = $('#niveles').val().trim();

  //Comprobar que se han seleccionado dimension y jerarquia
  if (nombreJerarquia.trim() === ''){
    var mensaje = i18next.t('seleccionaJer');
    toastr.error(mensaje);
    return;
  }

  if(nivelSeleccionado === null){
    return;
  }

  //Si no se ha dado nombre de nivel, le asignamos el de la columna
  if(nombreNivel.trim() ===''){
    nombreNivel = nivelSeleccionado;
  }

  //Comprobamos si el nivel ya se ha añadido
  var encontrado = false;
  
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia){
      const niveles = estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].niveles;

      if (niveles.includes(nivelSeleccionado)){
        encontrado = true;
        var mensaje = i18next.t('yaExisteNiv');
        toastr.error(mensaje);
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
    estructuraCubo.dimensiones[nombreDimension].jerarquias[nombreJerarquia].niveles.push(nivelSeleccionado);
  
    //Si es el primer nivel añadido, se guarda como nivel por defecto
    if (estructuraCubo.dimensiones[nombreDimension].jerarquias[nombreJerarquia].niveles.length === 1){
      estructuraCubo.dimensiones[nombreDimension].jerarquias[nombreJerarquia].nivel_actual = nivelSeleccionado;
    }
    
    var mensaje = i18next.t('exitoCrearNivel');
    toastr.success(mensaje);
    
    $('#niveles').val('');

    //Limpiamos el input después de añadir la jearquía
    $('#nombreNivel').val('');

    $('#niveles').val(null).trigger('change.select2');
    //Acutlizamos los cambios en el arbol
    actualizarSelectMedidas(nivelSeleccionado, 'añadir');
    añadirOrdenNiveles();
    actualizarArbol();
    //imprimirArbol();
    
  } 
}

//Función para añadir la selección de la jerarquia por defecto y el orden de los niveles
function añadirOrdenNiveles(){
  $('#contenedorDimensiones').empty();
  var titulo = $('<h5 data-i18n="tituloDefecto">' + i18next.t('tituloDefecto') + '</h5>');
  $('#contenedorDimensiones').append(titulo);
  
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
    var label = $('<label>' + dimension + '</label>' + '<br>');
    
    var dimensionContenedor = $('<div class="dimension-container"></div>');
    
    //Obtenemos la jerarquia de la dimension
    var jerarquias = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias);
    if (jerarquias.length === 0) return;

    var jerarquia = jerarquias[0];
    var niveles = estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].niveles || [];

    // Creamos select para seleccionar el nivel actual
    var selectNivelActual = $('<select class="form-control select-nivel-actual" id="nivelActual_' + dimension + '"></select><br>');
    niveles.forEach(function(nivel) {
      selectNivelActual.append('<option value="' + nivel + '">' + nivel + '</option>');
    });

    // Establecemos el valor por defecto al ultimo nivel, el mas especifico
    selectNivelActual.val(niveles[niveles.length - 1]);

    selectNivelActual.on('change', function() {
      var nuevoNivel = $(this).val();
      estructuraCubo.dimensiones[dimension].jerarquias[jerarquia]["nivel_actual"] = nuevoNivel;
    });

    //Creamos la lista ordenable para los niveles
    var lista = $('<ul class="lista-ordenable" id="ordenable_' + dimension + '"></ul>');
    niveles.forEach(function(nivel) {
      var item = $('<li id="' + nivel  + '">' + nivel + '</li>');
      lista.append(item);
    });

    dimensionContenedor.append(label);
    dimensionContenedor.append('<label data-i18n="labelOrden">' + i18next.t('labelOrden') + '</label>');
    dimensionContenedor.append(selectNivelActual);
    dimensionContenedor.append(lista);
    $('#contenedorDimensiones').append(dimensionContenedor);
    
    $('#jerarquiadefecto_' + dimension).select2({
      minimumResultsForSearch: Infinity,
      
    });

    $('#nivelActual_'+ dimension).select2({
      minimumResultsForSearch: Infinity,
    });

     $('#nivelActual_' + dimension).on('change', function() {
      actualizarArbol();
    });

    $('#jerarquiadefecto_' + dimension).on('change', function() {
      actualizarArbol();
    });
   
    $('#ordenable_' + dimension).sortable();
    $('#ordenable_' + dimension).disableSelection();
  });

  $('#contenedorDimensiones').append('<button data-i18n="botonOrden" type="button" onclick="aplicarOrden()" class="btn btn-block btn-primary"\
    style="width: 20%; float: right;">' + i18next.t('botonOrden') + '</button>');

}

// Función que coge los valores de niveles de la lista ordenable 
// y los ordena segun la lista en el array de valores
function aplicarOrden(){
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
    const jerarquias = Object.keys(estructuraCubo.dimensiones[dimension].jerarquias);
    if (jerarquias.length === 0) return;

    const jerarquia = jerarquias[0]; // asumimos 1 jerarquía por dimensión
    const listaOrdenable = $(`#ordenable_${dimension}`);
    if (listaOrdenable.length === 0) return;

    // Recogemos el orden actual de los <li> en la lista
    const nuevoOrden = [];
    listaOrdenable.children('li').each(function() {
      nuevoOrden.push(this.id);  // Cada li tiene como id el nombre del nivel
    });

    // Actualizamos el array de niveles en la estructura
    estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].niveles = nuevoOrden;

    //Actualizamos el valor del nivel actual
    var nivelActualSeleccionado = $('#nivelActual_' + dimension).val();

    if (nivelActualSeleccionado){
      estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual = nivelActualSeleccionado;
    }
     });

  toastr.success("Orden actualizado correctamente");
  actualizarArbol();
  imprimirArbol();
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

    var mensaje = i18next.t('eliminarDim');
    toastr.success(mensaje);

    //Eliminamos la dimensión del select
    $("#dimensiones").find('option[value="' + dimension + '"]').remove();
    $('#dimensiones').val(null).trigger('change.select2');

    //Ocultamos el modal
    $('#modalDimension').modal('hide')

    //Actualizamos el arbol
    actualizarDimensiones();
    actualizarJerarquias();
    actualizarArbol();
    //imprimirArbol();
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

  var mensaje = i18next.t('eliminarJer');
  toastr.success(mensaje);

  //Ocultamos el modal
  $('#modalJerarquia').modal('hide');

  //imprimirArbol();
  //Actualizamos el select de jerarquias
  actualizarJerarquias();
  añadirOrdenNiveles();

  //Actualizamos el arbol
  actualizarArbol();
  
}

//Función que elimina nivel
function eliminarNivel(){
  
  //Recuperamos el nivel seleccionado para borrar
  var nivel = $('#niveles').val();

  //Ocultamos el modal
  $('#modalNivel').modal('hide');

  //Comprobamos que el nivel existe en el estructura, si existe lo borra
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {

    Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {

      let niveles = estructuraCubo.dimensiones[dimension].jerarquias[jerarquia].niveles;
      // Comprobamos que el nivel exista en el array de niveles de la jerarquia
      const index = niveles.indexOf(nivel);

      // Lo eliminamos si existe
      if (index !== -1){
        niveles.splice(index, 1);
        var mensaje = i18next.t('eliminarNiv');
        actualizarSelectMedidas(nivel, 'eliminar');
        toastr.success(mensaje);
      }
      else {
        var mensaje = i18next.t('noPerteneceNiv');
        toastr.error(mensaje);
      }
    });
  });

  
  //Actualizamos el select de medidas
  actualizarSelectMedidas(nivel, 'eliminar');
  
  //Actualizamos el arbol
  añadirOrdenNiveles();
  actualizarArbol();
  //imprimirArbol();
}

// Función que actualiza el select de medidas
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

//Función que actualiza la vista de árbol del cubo
function actualizarArbol(){

  // Borramos el árbol actual
  var tree = $.ui.fancytree.getTree("#tree");

  if (!tree) {
  return;
  }

  var rootNode = tree.getRootNode();

  if (!rootNode) {
  return;
}

  tree.getRootNode().removeChildren();

  // Iteramos por las dimensiones
  Object.keys(estructuraCubo.dimensiones).forEach(function(dimension) {
    // Creamos nodo para la dimensión
    var nodoDimension = rootNode.addChildren({
      title: dimension,
      tipo: "Dimension",
      extraClasses: "fancytree-dimension",
      icon: "icono-dimension",
    });

    tree.expandAll();  

    var jerarquias = estructuraCubo.dimensiones[dimension].jerarquias;
    var jerarquiaNombre = Object.keys(jerarquias)[0]; // Solo hay una
    var jerarquiaPorDefecto = estructuraCubo.dimensiones[dimension].jerarquia_por_defecto;

    //var niveles = jerarquias[jerarquia].niveles || [];
    if (!jerarquiaNombre){
      return;
    }

    // Iteramos sobre todas las jerarquías 
    Object.keys(jerarquias).forEach(function(jerarquia) {
      var nodoJerarquia = nodoDimension.addChildren({
        title: jerarquiaNombre,
        tipo: jerarquia === jerarquiaPorDefecto ? "Jerarquia por defecto" : "Jerarquia",
        extraClasses: jerarquia === jerarquiaPorDefecto
          ? "fancytree-jerarquia-defecto"
          : "fancytree-jerarquia",
        icon: "icono-jerarquia",
      });

      var niveles = jerarquias[jerarquiaNombre].niveles;
      
      // Si no hay niveles, no añadimos nada
      if (!Array.isArray(niveles) || niveles.length === 0) {
        return;
      }

      // Obtenemos y recorremos los niveles de esta jerarquía
      niveles.forEach(function(nivel) {
        nivelActual = jerarquias[jerarquia].nivel_actual;
        console.log("En actualizar arbol, el nivel actual es: " + nivelActual);
        const esActual = nivel === nivelActual;
        const tituloConFlecha = esActual
          ? `<span class="titulo-nivel">${nivel}</span><span class="emoji-flecha">🠔</span>`
          : nivel;

        nodoJerarquia.addChildren({
          title: tituloConFlecha,
          tipo: esActual ? "Nivel actual" : "Nivel",
          extraClasses: esActual 
            ? "fancytree-nivel-actual"
            : "fancytree-nivel",
          icon: "icono-nivel",
        });
      });
    });
  });

  tree.expandAll();
}

/*
// Función que imprime el cubo por consola
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
}*/

//Función que comprueba que no haya jerarquías vacías antes de guardar el cubo
function comprobarJerarquiasVacias(){

  //Iteramos sobre cada dimensión
  for (var dimension in estructuraCubo.dimensiones) {

    //Comprobamos si la dimensión tiene jerarquías
    if (Object.keys(estructuraCubo.dimensiones[dimension].jerarquias).length === 0) {
      var mensaje = i18next.t('dimensionSinCompletar', {nombre: dimension});
      toastr.error(mensaje);
      return true;
    }
    else {

      //Iteramos sobre cada jerarquía
      for (var jerarquia in estructuraCubo.dimensiones[dimension].jerarquias) {

        //Comprobamos si la jerarquía tiene al menos un nivel
        if (Object.keys(estructuraCubo.dimensiones[dimension].jerarquias[jerarquia]).length === 0) {
          var mensaje = i18next.t('JerarquiaSinCompletar', {nombre: jerarquia});
          toastr.error(mensaje);
            return true;
        }
      } 
    }   
  } 

  //Si todas las jerarquías tienen al menos un nivel, devolvemos false
  return false;
}

// Función que realiza la petición para crear el cubo
function enviarCubo(){

  actualizarArbol();

  var vacias = comprobarJerarquiasVacias();
 
  nombreCubo = $('#cubename').val();
  nombreExperimentacion = $("#experimentaciones").val()
  nombreExperimentacion = nombreExperimentacion.match(/\/\s*([^\/]+)/)[1];
  descripcion = $('#description').val();
  nombreMedida = $('#nombreMedida').val();
  medida = $('#columnasSeleccionadas').val();
  medidaSeleccionada = $('#medidas').val();

  console.log("IMPRIMIENDO VALORES FINALES");
  console.log("Nombre cubo: " + nombreCubo);
  console.log("nombre experimentacion: " + nombreExperimentacion);
  console.log("medida: " + medida);

  switch (medidaSeleccionada){
    case 'suma': 
      tipoMedida = "SUM";
      break;
    case 'maximo':
      tipoMedida = "MAX";
      break;
    case 'minimo':
      tipoMedida = "MIN";
      break;
    case 'promedio':
      tipoMedida = "AVG";
      break;
    default: 
      tipoMedida = "SUM";
  }

  cubo = {user, date, nombreCubo, descripcion, nombreExperimentacion, ...estructuraCubo, nombreMedida, medida, tipoMedida};

  // Obtenemos el token CSRF del documento HTML
  var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

  //Realizamos petición ajax
  cubo_json = JSON.stringify(cubo);
  console.log("Cubo en json");
  console.log(cubo_json);

  $.ajax({
    url: "/analisismultidimensional/crear-cubo", 
    headers: {
      'X-CSRFToken': csrfToken
    },
    type: "POST",
    data: {'cubo': JSON.stringify(cubo)},
    dataType: 'json',
    success: function(data) {
      console.log(data)
      if(data.success){
         var mensaje = i18next.t('exitoCrearCubo');
         toastr.success(mensaje);
      } else {
         var mensaje = i18next.t('yaExisteCubo');
         toastr.error(mensaje);
      }
    }
  });

  }
