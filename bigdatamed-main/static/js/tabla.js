console.log("Se va a realizar la petición ajax para obtener cubos");
//Obtenemos los cubos
var grid;
var csrfToken;


function compararFechas(fecha1, fecha2) {
  // Acceder al campo 'date' de cada objeto JSON
  const fecha1Str = fecha1.date;
  const fecha2Str = fecha2.date;

  // Dividir las fechas en componentes y convertirlas a números
  const fecha1Parts = fecha1Str.split('/');
  const fecha2Parts = fecha2Str.split('/');

  const fecha1Year = parseInt(fecha1Parts[2]);
  const fecha1Month = parseInt(fecha1Parts[1]);
  const fecha1Day = parseInt(fecha1Parts[0]);

  const fecha2Year = parseInt(fecha2Parts[2]);
  const fecha2Month = parseInt(fecha2Parts[1]);
  const fecha2Day = parseInt(fecha2Parts[0]);

  // Comparar fechas por año, mes y día (orden descendente)
  if (fecha1Year > fecha2Year) {
      return -1;
    } else if (fecha1Year < fecha2Year) {
      return 1;
    } else if (fecha1Month > fecha2Month) {
      return -1;
    } else if (fecha1Month < fecha2Month) {
      return 1;
    } else if (fecha1Day > fecha2Day) {
      return -1;
    } else {
      return 0; // Fechas iguales
    }
}


//Realizamos petición ajax a la vista que realiza la petición a la API
$.ajax({
    url: "/analisismultidimensional/obtener-cubos", 
    dataType: 'json',  
}).then(function(data) {
    console.log("El array de tablas de la view es:");
    console.log(data);
    
    //Convertimos el objeto que nos devuelve la petición en array, para su posterior ordenación
    var dataArray = Object.values(data);
    console.log("Objeto convertido");
    console.log(dataArray);

    //Utilizamos sólo el campo propiedades para la tabla
    //Como la petición devuelve un array, y cada cubo es otro array, accedemos al campo "propiedades" de cada cubo
    var propiedadesArray = dataArray[0].map(function(cubo) {
      console.log("Enseñando propiedades");
      console.log(cubo.propiedades)
      return cubo.propiedades;
    });

    console.log(propiedadesArray);
    //Añadimos al array, un atributo icono, que se mostrará en la tabla
    var propiedadesArrayCompleto = propiedadesArray.map(function(cubo) {
      return {
        ...cubo,
        icono: '<i class="fas fa-search"></i>'
      };
    });
    //dataCubos.sort(compararFechas);
    inicializarFancyGrid(propiedadesArrayCompleto);
     // Obtenemos el token CSRF del documento HTML
    csrfToken = $('input[name="csrfmiddlewaretoken"]').val();


  
});

//{"user": "antonio", "date": "10/2/2024", "nombreCubo": "holasd", "nombreExperimentacion": "Prueba 4", "dimensiones": {"dim1": {"jerarquias": {"jer1": {"HOSPITAL": "sda"}}}, "dim2": {"jerarquias": {"jer2": {"AMBITO": "ddd"}}}}, "nombreMedida": "pepon", "medida": "IDENTIF", "tipoMedida": "Promedio (AVG)"}





//Una vez que tenemos los cubos, creamos la tabla



//Ordenamos los cubos de más reciente a más antiguo


function inicializarFancyGrid(data){
  grid = new FancyGrid({
    height: 500,
    title: '',
    hideCopyrightImage: true,
    selModel: {
        type: 'row',
        allowDeselect: true,
        paging: {
            pageSize: 10,
            pageSizeData: [5,10,20]
        },
    },
    rowTrackOver: true,
    paging: true,
    defaults: {      
      resizable: true,
      draggable: true,
    },
    theme: 'bootstrap',
    renderTo: 'container',
    data: data,
    autoLoad: true,
    columns: [
        {
            index: 'nombreCubo',
            title: 'Nombre Cubo',
            type: 'string',
            width: 250
        },
        {
            index: 'nombreExperimentacion',
            title: 'Experimentación',
            type: 'string',
            width: 250
        },
        {
            index: 'date',
            title: 'Fecha creación',
            type: 'string',
            sortable: true,
            width: 200,
            filter: {
                type: 'date',
                header: true
            },
        },
        {
            index: 'descripcion',
            title: 'Descripción',
            type: 'string',
            width: 500
        },
        {
          index: 'icono',
            title: ' ',
            type: 'string',
            width: 40
        }

    ],
    events: [{
        rowclick: function(grid, o) {
            var cubo = o.data;
            // Accede a la fila seleccionada aquí, por ejemplo:
            console.log("Datos obtenidos del cubo");
            console.log(cubo);
            var infoElement = document.getElementById('info');
            infoElement.textContent = "Nombre Cubo: " + cubo.nombreCubo + ", Experimentación: " + 
            cubo.nombreExperimentacion + ", Fecha creación: " + cubo.date;

           // window.location.href = "/cubo-info?cuboData=" + encodeURIComponent(cubo);
        },
        cellclick: function(grid, o) {
          var columnIndex = o.columnIndex;
          
          //Si se hace clic en la lupa, realiza la petición a la vista para mostrar
          //la página con la información del cubo
          if(columnIndex === grid.columns.length -1){
            var cubo = o.data;
            //console.log(cubo);
            var cuboencoded = btoa(JSON.stringify(cubo));
            console.log(cuboencoded);

            var cubodecoded = atob(cuboencoded);
            console.log(cubodecoded);

            window.open('/analisismultidimensional/cubo-info?cubo=' + encodeURIComponent(cuboencoded));
            /*
            $.ajax({
              url: "/analisismultidimensional/cubo-info",
              data: {'cubo': JSON.stringify(cubo)},
              dataType: "json",
            }).always(function(data){
              console.log("DATOS RECIBIDOS");
              console.log(data);
              window.open('/analisismultidimensional/cubo-info', '_blank');
            })
              */

          }
        }
    }]

    
  });
}

/*
document.addEventListener("DOMContentLoaded", function() {

    

});*/

