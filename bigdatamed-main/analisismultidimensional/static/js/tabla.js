
var cubo = {
  "descripcion":"algo",
  "nombreCubo": "algo"
}


inicializarTraducciones();

function actualizarColumnas(){
  const grid = FancyGrid.get('container');
  if(grid){
    grid.setColumnTitle('nombreCubo', i18next.t('columnaNombre'));
    grid.setColumnTitle('nombreExperimentacion', i18next.t('columnaExp'));
    grid.setColumnTitle('date', i18next.t('columnaFecha'));
    grid.setColumnTitle('descripcion', i18next.t('columnaDesc'));
  }
}

$(document).ready(async function(){
 
  $('body').localize();

  const flagsElement = document.getElementById("flags");
  flagsElement.addEventListener("click", (e) => {
    actualizarColumnas();
  })
});



console.log("Se va a realizar la petición ajax para obtener cubos");
//Obtenemos los cubos
var grid;
var csrfToken;


function compararFechas(fecha1, fecha2) {
  // Accedemos al campo 'date' de cada objeto JSON
  const fecha1Str = fecha1.date;
  const fecha2Str = fecha2.date;

  // Dividimos las fechas en componentes y las convertimos a números
  const fecha1Part = fecha1Str.split('/');
  const fecha2Part = fecha2Str.split('/');

  const fecha1Year = parseInt(fecha1Part[2]);
  const fecha1Month = parseInt(fecha1Part[1]);
  const fecha1Day = parseInt(fecha1Part[0]);

  const fecha2Year = parseInt(fecha2Part[2]);
  const fecha2Month = parseInt(fecha2Part[1]);
  const fecha2Day = parseInt(fecha2Part[0]);

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
    
    //Convertimos el objeto que nos devuelve la petición en array, para su posterior ordenación
    var dataArray = Object.values(data);

    //Utilizamos sólo el campo propiedades para la tabla
    //Como la petición devuelve un array, y cada cubo es otro array, accedemos al campo "propiedades" de cada cubo
    var propiedadesArray = dataArray[0].map(function(cubo) {
      return cubo.propiedades;
    });

    //Añadimos al array, un atributo icono, que se mostrará en la tabla
    var propiedadesArrayCompleto = propiedadesArray.map(function(cubo) {
      return {
        ...cubo,
        icono: '<i class="fas fa-search"></i>'
      };
    });
  
    inicializarFancyGrid(propiedadesArrayCompleto);
  
     // Obtenemos el token CSRF del documento HTML
    csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
});

//Una vez que tenemos los cubos, creamos la tabla
function inicializarFancyGrid(data){
  grid = new FancyGrid({
    renderTo:'container',
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
            title: i18next.t('columnaNombre'),
            type: 'string',
            width: 250
        },
        {
            index: 'nombreExperimentacion',
            title: i18next.t('columnaExp'),
            type: 'string',
            width: 250
        },
        {
            index: 'date',
            title: i18next.t('columnaFecha'),
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
            title: i18next.t('columnaDesc'),
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
            // Accedemos a la fila seleccionada aquí
            var infoElement = document.getElementById('info');
            infoElement.textContent = "Nombre Cubo: " + cubo.nombreCubo + ", Experimentación: " + 
            cubo.nombreExperimentacion + ", Fecha creación: " + cubo.date;

        },
        cellclick: function(grid, o) {
          var columnIndex = o.columnIndex;
          
          //Si se hace clic en la lupa, realiza la petición a la vista para mostrar
          //la página con la información del cubo
          if(columnIndex === grid.columns.length -1){
            var cubo = o.data;
            var cuboencoded = btoa(JSON.stringify(cubo));
            var cubodecoded = atob(cuboencoded);
          
            window.open('/analisismultidimensional/cubo-info?cubo=' + encodeURIComponent(cuboencoded));

          }
        }
    }]

    
  });
}


