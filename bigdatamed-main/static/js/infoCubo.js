/*var cubo = {"user": "antonio", "date": "12/03/2024", "nombreCubo": "Test 3", "descripcion": "Esto es una prueba 3", 
"nombreExperimentacion": "Prueba 4", "dimensiones": {"Dimension1": {"jerarquias": {"Jer11": {"HOSPITAL": "hosp"}}}, 
"Dimension2": {"jerarquias": {"jer22": {"AMBITO": "ambit"}}}, "dimension3": {"jerarquias": {"jer33": {"IDENTIF": "identificador"}}}}, 
"nombreMedida": "medida ejemplo", "medida": "TIPCIP", "tipoMedida": "M\u00ednimo (MIN)"};
*/

//Función que se llama para borrar un cubo
async function borrarCubo(){

  //Recuperamos el nombre del cubo
  nombrecubo = cubo.nombreCubo;

  const confirmar = confirm("Estás seguro de que deseas eliminar el cubo " + nombrecubo + '?');
  if(!confirmar) {
    return;
  }

 

  //URL del endpoint para la petición DELETE
  const url = 'http://servicios_olap:8001/analisismultidimensional/deleteCube/' + nombrecubo;
  console.log(url);

  //Hacemos la petición
  try{
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
       }
    })

    if(response.ok) {
      const resultado = await response.json();
      console.log(resultado.message);
    }
    else {
      const error = await response.json()
      console.log(error.message);
    }
    window.close();
  } catch (error){
    console.log('Error: ' + error.message);
  }

 
  
}

function procesarOperacion(operacion){

  switch(operacion){
    case "drilldown":
      
      console.log("Cubo: ", cubo)

      console.log("Dimensiones: ", cubo.dimensiones);


      //Encontramos las dimensiones que tienen más de una jerarquía, para poder aplicar la operación
      var dimnensionesMultiples = {}


      //Para cada dimensión comprobamos que haya más de una jerarquía
      for (let dimension in cubo.dimensiones) {
        var jerarquias = cubo.dimensiones[dimension].jerarquias


        if (Object.keys(jerarquias).length > 1){
          dimnensionesMultiples[dimension] = Object.keys(jerarquias)
        }
      }

      if (Object.keys(dimnensionesMultiples).length == 0){
        if(language === 'es')
          toastr.error("No hay dimensiones a las que aplicar la operación");
        else
          toastr.error("There are no dimensions to apply the operation to");
       
        return;
      }

      console.log("Dimensiones multiples: " + dimnensionesMultiples)

      $('#contenedorSelectsDrilldown').empty();

      var divselectDimension = $('<div></div>');

      var selectDimension = $('<select class="form-control select2" id="selectDimension"></select>' + '<br><br>');

      for (let dimension in dimnensionesMultiples) {
        var option = new Option(dimension, dimension, false, false)
        selectDimension.append(option)
      }

      divselectDimension.append('<label data-section="operations" data-value="labelSelectDimension">Selecciona la dimensión a la que aplicar la operación</label>');
      divselectDimension.append(selectDimension);
      divselectDimension.append('<button type="button" onclick="realizarDrillDown()" class="btn btn-block btn-primary" style="width: 20%; float: right;">Aplicar operación</button>');
      $('#contenedorSelectsDrilldown').append(divselectDimension);

      $('#selectDimension').select2({
        minimumResultsForSearch: Infinity,
        
      });

      $('#selectDimension').on('change', function() {
        console.log("Esta cambiando el valor de la dimension seleccionada");
      });


      break;
  }
}

function realizarDrillDown(){
  console.log("Realizando drilldown");
  var dimension = $('#selectDimension').val();
  console.log("Con la dimensión; ", dimension)

  delete cubo.id;
  delete cubo.icono;

  var cuboFinal = {
    "propiedades": cubo,
    "dimension": dimension
  };


  console.log("Cubo final ", JSON.stringify(cuboFinal))

  console.log("Haciendo peticion a la API");

  fetch('http://localhost:8001/analisismultidimensional/drilldown/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(cuboFinal),

  })
  .then(response => {
    response.json();
    console.log("Respuesta de la api: ", response);

    if(response.statusText == "Bad Request"){
      if(language === 'es')
        toastr.error("No hay una jerarquía más específica para realizar drill down");
      else
        toastr.error("No more specific hierarchy available for drill-down");
    }
  })
}


var tree = $('#tree');
var cubo;

$(document).ready(function(){


    $('#operaciones').select2({
      minimumResultsForSearch: Infinity
    });

    $('#operaciones').on('change', function() {
      var selected = $(this).val();
      procesarOperacion(selected);
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
        // Actualizar el contenido del span con la información del nodo activado

        $("#infonodo").text("Tipo de nodo: " + tipoNodo);
        $("#infovalor").text("Nombre: " + contenidoNodo);
        //$("#info").text("Contenido: " + contenidoNodo);
      },
    });
  
    tree = $.ui.fancytree.getTree("#tree");
    
    //Recuperamos el valor del cubo
    var parametrosURL = new URLSearchParams(window.location.search);
    var dataCuboEncoded = parametrosURL.get('cubo');
    var dataCuboDecoded = atob(dataCuboEncoded);
    cubo = JSON.parse(dataCuboDecoded);

    console.log(cubo);

    $("#descripcion").text("Descripción: " + cubo.nombreCubo);

    if(language === 'es'){
      $("#nombrecubo").text("Nombre del cubo: " + cubo.nombreCubo);
      $("#descripcion").text("Descripción: " + cubo.descripcion);
      console.log("es");
    }
    else {
      $("#nombrecubo").text("Cube name: " + cubo.nombreCubo);
      $("#descripcion").text("Description: " + cubo.descripcion);
      console.log("en");
    }
    imprimirArbol();
    actualizarArbol();

    /*
    $("#tree").on("fancytreeactivate", function(event, data) {
      // Obtener el nodo activado
      var nodo = data.node;
      // Obtener el tipo de nodo y su contenido
      var tipoNodo = nodo.data.tipo;
      var contenidoNodo = nodo.title;

      // Actualizar el contenido del span con la información del nodo activado
      $("#infonodo").text("Tipo de nodo: " + tipoNodo);
      $("#infovalor").text("Valor: " + contenidoNodo);
      //$("#info").text("Contenido: " + contenidoNodo);
  });
*/

  });

  
  function actualizarArbol(){

    //Borramos el árbol actual
    var tree = $.ui.fancytree.getTree("#tree");
    tree.getRootNode().removeChildren();
    
    //Iteramos por las dimensiones
    Object.keys(cubo.dimensiones).forEach(function(dimension) {
  
      console.log("Dentro de la dimension: " + dimension);
      // Creamos nodo para la dimensión
      tree.getRootNode().addChildren({
      title: dimension,
      tipo: "Dimension",
      extraClasses: "fancytree-dimension ",
      icon: "icono-dimension",
      // Otras opciones de nodo
      });
  
      tree.expandAll();  
  
      // Iteramos sobre las jerarquías de la dimensión
      Object.keys(cubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {
  
          console.log("Dentro de la jerarquia: " + jerarquia);
          // Creamos nodo para la jerarquía
          var nodoDimension = tree.findFirst(dimension);
        
          if(nodoDimension){
            if(cubo.dimensiones[dimension].jerarquia_por_defecto == jerarquia){
              nodoDimension.addChildren({
                title: jerarquia,
                tipo: "Jerarquia por defecto",
                extraClasses: "fancytree-jerarquia-defecto",
                icon: "icono-jerarquia",
              });
            }
            else {
              nodoDimension.addChildren({
                title: jerarquia,
                tipo: "Jerarquia",
                extraClasses: "fancytree-jerarquia",
                icon: "icono-jerarquia",
              });
            }
            tree.expandAll();
          }
  
          // Iteramos sobre los niveles de la jerarquia
          var niveles = Object.keys(cubo.dimensiones[dimension].jerarquias[jerarquia]);
          
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
                    title: cubo.dimensiones[dimension].jerarquias[jerarquia][nivel] + ' - ' + nivel,
                    tipo: "Nivel",
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
  
    console.log("Imprimiendo árbol");
  
    Object.keys(cubo.dimensiones).forEach(function(dimension) {
  
      console.log("Dimensión: " + dimension)
      // Iteramos sobre las jerarquías de la dimensión
      Object.keys(cubo.dimensiones[dimension].jerarquias).forEach(function(jerarquia) {
  
          console.log("Jerarquia: " + jerarquia);
          // Iteramos sobre los niveles de la jerarquia
          var niveles = Object.keys(cubo.dimensiones[dimension].jerarquias[jerarquia]);
  
          niveles.forEach(function(nivel) {
  
            console.log("Nivel: " + nivel);
              
          });
      });
  
    });
  
    console.log("Arbol acabado");
  
    console.log(cubo.dimensiones);
  }
  
  
  