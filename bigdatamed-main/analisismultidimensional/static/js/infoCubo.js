/*var cubo = {"user": "antonio", "date": "12/03/2024", "nombreCubo": "Test 3", "descripcion": "Esto es una prueba 3", 
"nombreExperimentacion": "Prueba 4", "dimensiones": {"Dimension1": {"jerarquias": {"Jer11": {"HOSPITAL": "hosp"}}}, 
"Dimension2": {"jerarquias": {"jer22": {"AMBITO": "ambit"}}}, "dimension3": {"jerarquias": {"jer33": {"IDENTIF": "identificador"}}}}, 
"nombreMedida": "medida ejemplo", "medida": "TIPCIP", "tipoMedida": "M\u00ednimo (MIN)"};
*/
let condicionesDiceLogico = [];
var cubo;
var dimensionesDisponiblesDD = {};
var dimensionesDisponiblesRU = {};
var dimensionesDice = [];
var valoresDice = {};

let diceChart = null;

//Función que se llama para borrar un cubo
async function borrarCubo(){

  //Recuperamos el nombre del cubo
  nombrecubo = cubo.nombreCubo;
  user = cubo.user;

  const confirmar = confirm("Estás seguro de que deseas eliminar el cubo " + nombrecubo + '?');
  if(!confirmar) {
    return;
  }

  //URL del endpoint para la petición DELETE
  //const url = `http://localhost:8001/analisismultidimensional/deleteCube/?user=${user}&nombre_cubo=${nombrecubo}`;
  const url = `http://servicios_olap:8001/analisismultidimensional/deleteCube/?user=${user}&nombre_cubo=${nombrecubo}`;
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

//Función que crea los select para la operación drill down
function crearOpcionesDrillDown() {
  console.log("Se ha seleccionado la operación de drill-down");

  $('#contenedorSelects').empty();

  const divselectDimension = $('<div></div>');
  const selectDimension = $('<select class="form-control select2" id="selectDimensionDrill"></select><br><br>');

  selectDimension.append($('<option value="" disabled selected></option>'));

  for (let dimension in cubo.dimensiones) {
    const jerarquiaPorDefecto = cubo.dimensiones[dimension].jerarquia_por_defecto;
    const niveles = cubo.dimensiones[dimension].jerarquias[jerarquiaPorDefecto].niveles;
    const nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquiaPorDefecto].nivel_actual;
    const jerarquia = cubo.dimensiones[dimension].jerarquia_por_defecto;

    const idxActual = niveles.indexOf(nivelActual);
    if (idxActual < niveles.length - 1) {
      const option = new Option(dimension, dimension, false, false);
      selectDimension.append(option);
    }
  }

  divselectDimension.append('<label data-i18n="labelSelectDimension">' + i18next.t('labelSelectDimension') + '</label>');
  divselectDimension.append(selectDimension);
  $('#contenedorSelects').append(divselectDimension);

  $('#selectDimensionDrill').select2({ minimumResultsForSearch: Infinity });

  $('#selectDimensionDrill').on('change', function () {
     $('#subopcionesDrillDown').remove();
     $('#diceChart').empty();
    const dimension = $(this).val();
    const jerarquia = cubo.dimensiones[dimension].jerarquia_por_defecto;
    const niveles = cubo.dimensiones[dimension].jerarquias[jerarquia].niveles;
    const nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual;

    const idxActual = niveles.indexOf(nivelActual);
    const nivelesEspecificos = niveles.slice(idxActual + 1); // Del siguiente al actual hacia más específico

    $('#selectNivelInferior').remove();
    $('#divselectNivelInferior').remove();
    $('#divselectJerarquia').remove();
    $('#selectJerarquia').remove();

     const subContenedor = $('<div id="subopcionesDrillDown"></div>');

    const divJerarquia = $('<div id="divselectJerarquia"></div>');
    const selectJerarquia = $('<select class="form-control select2" id="selectJerarquia"></select><br><br>');
    const optionJerarquia = new Option(jerarquia, jerarquia, false, false)
    selectJerarquia.append(optionJerarquia)
    divJerarquia.append('<label data-i18n="labelSelectJerarquia">' + i18next.t('labelSelectJerarquia') + '</label>');
    divJerarquia.append(selectJerarquia)
    $('#contenedorSelects').append(divJerarquia);

    const divNivel = $('<div id="divselectNivelInferior"></div>');
    const selectNivel = $('<select class="form-control select2" id="selectNivelInferior"></select><br><br>');
    selectNivel.append($('<option value="" disabled selected></option>'));

    nivelesEspecificos.forEach(n => {
      const option = new Option(n, n, false, false);
      selectNivel.append(option);
    });

    divNivel.append('<label data-i18n="labelSelectNivel">' + i18next.t('labelSelectNivel') + '</label>');
    divNivel.append(selectNivel);

    const boton = $(`
    <button data-i18n="botonDD" type="button" onclick="realizarDrillDown()" 
      class="btn btn-block btn-primary" style="width: 35%; float: right;">
      ${i18next.t('botonDD')}
    </button>`);

    //Añadimos al contenedor
    subContenedor.append(divJerarquia);
    subContenedor.append(divNivel);
    subContenedor.append(boton);

    $('#contenedorSelects').append(subContenedor);

    $('#selectNivelInferior').select2({ minimumResultsForSearch: Infinity });

    $('#selectJerarquia').select2({ minimumResultsForSearch: Infinity });
  });
}

//Función que crea los select para la operación roll up
function crearOpcionesRollUp() {
  console.log("Se ha seleccionado la operación de rollup");

  $('#contenedorSelects').empty();

  const divselectDimension = $('<div></div>');
  const selectDimension = $('<select class="form-control select2" id="selectDimension"></select><br><br>');

  selectDimension.append($('<option value="" disabled selected></option>'));

  // Añadir dimensiones con al menos 2 niveles y que no estén en el nivel más general
  for (let dimension in cubo.dimensiones) {
    const jerarquiaPorDefecto = cubo.dimensiones[dimension].jerarquia_por_defecto;
    const niveles = cubo.dimensiones[dimension].jerarquias[jerarquiaPorDefecto].niveles;
    const nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquiaPorDefecto].nivel_actual;

    const idxActual = niveles.indexOf(nivelActual);
    if (idxActual > 0) {
      const option = new Option(dimension, dimension, false, false);
      selectDimension.append(option);
    }
  }

  divselectDimension.append('<label data-i18n="labelSelectDimension">' + i18next.t('labelSelectDimension') + '</label>');
  divselectDimension.append(selectDimension);
  $('#contenedorSelects').append(divselectDimension);

  $('#selectDimension').select2({ minimumResultsForSearch: Infinity });

  $('#selectDimension').on('change', function () {
    $('#diceChart').empty();

    $('#subopcionesRollup').remove();
    const dimension = $(this).val();
    const jerarquia = cubo.dimensiones[dimension].jerarquia_por_defecto;
    const niveles = cubo.dimensiones[dimension].jerarquias[jerarquia].niveles;
    const nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual;

    const idxActual = niveles.indexOf(nivelActual);
    const nivelesGenerales = niveles.slice(0, idxActual); // Del más general hasta justo antes del actual

    // Limpiar y crear select de nivel superior
    $('#selectNivelSuperior').remove();
    $('#divselectNivelSuperior').remove();
    $('#divselectJerarquia').remove();
    $('#selectJerarquia').remove();

    const subContenedor = $('<div id="subopcionesRollup"></div>');

    const divJerarquia = $('<div id="divselectJerarquia"></div>');
    const selectJerarquia = $('<select class="form-control select2" id="selectJerarquia"></select><br><br>');
    const optionJerarquia = new Option(jerarquia, jerarquia, false, false)
    selectJerarquia.append(optionJerarquia)
    divJerarquia.append('<label data-i18n="labelSelectJerarquia">' + i18next.t('labelSelectJerarquia') + '</label>');
    divJerarquia.append(selectJerarquia)
    //$('#contenedorSelects').append(divJerarquia);

    const divNivel = $('<div id="divselectNivelSuperior"></div>');
   
    const selectNivel = $('<select class="form-control select2" id="selectNivelSuperior"></select><br><br>');
    selectNivel.append($('<option value="" disabled selected></option>'));
    
    

    nivelesGenerales.forEach(n => {
      const option = new Option(n, n, false, false);
      selectNivel.append(option);
    });
  
    
    divNivel.append('<label data-i18n="labelSelectNivel">' + i18next.t('labelSelectNivel') + '</label>');
    divNivel.append(selectNivel);

    const boton = $(`
    <button data-i18n="botonRU" type="button" onclick="realizarRollUp()" 
      class="btn btn-block btn-primary" style="width: 35%; float: right;">
      ${i18next.t('botonRU')}
    </button>`);

    //Añadimos al contenedor
    subContenedor.append(divJerarquia);
    subContenedor.append(divNivel);
    subContenedor.append(boton);

    // Añadimos al contenedor principal
    $('#contenedorSelects').append(subContenedor);

    $('#selectNivelSuperior').select2({ minimumResultsForSearch: Infinity });

    $('#selectJerarquia').select2({ minimumResultsForSearch: Infinity });
  });
}

//Función que crea los select para la operación dice
function crearOpcionesDice() {
  console.log("Se ha seleccionado la operación de dice");
  $('#contenedorSelects').empty();
  condicionesDice = {};  // Reset

  const selectContainer = $('<div id="selectsDiceContainer"></div>');
  $('#contenedorSelects').append(selectContainer);

  // Función que añade un nuevo bloque de selección
  function añadirBloqueSeleccion() {
    const bloque = $('<div class="bloque-seleccion"></div>');

    // Select de dimensión
    const selectDimension = $('<select class="form-control select2 selectDimension"></select>');
    selectDimension.append('<option value="" disabled selected>Selecciona dimensión</option>');

    Object.keys(cubo.dimensiones).forEach(dimension => {
      // Solo permitir dimensiones no ya seleccionadas
      if (!(dimension in condicionesDice)) {
        selectDimension.append(new Option(dimension, dimension));
      }
    });

    bloque.append('<label>Dimensión:</label>');
    bloque.append(selectDimension);

    const selectValor = $('<select class="form-control select2 selectValor" disabled></select>');
    bloque.append('<label>Valor:</label>');
    bloque.append(selectValor);

    selectContainer.append(bloque);

    // Manejo del cambio en dimensión
    selectDimension.on('change', async function () {
       $('#diceChart').empty();
      const dimension = $(this).val();
      const jerarquia = cubo.dimensiones[dimension].jerarquia_por_defecto;
      const nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual;

      // Petición para obtener valores del nivel actual
      try {
        //const response = await fetch(`http://localhost:8001/analisismultidimensional/getLevels/?nombreCubo=${cubo.nombreCubo}&nombreUser=${cubo.user}&nombreJerarquia=${jerarquia}&nombreNivel=${nivelActual}`);
        const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/getLevels/?nombreCubo=${cubo.nombreCubo}&nombreUser=${cubo.user}&nombreJerarquia=${jerarquia}&nombreNivel=${nivelActual}`);

        const data = await response.json();
        const valores = [...new Set(data.valores)];

        selectValor.empty().prop("disabled", false).append('<option disabled selected>Selecciona valor</option>');
        valores.forEach(valor => {
          selectValor.append(new Option(valor, valor));
        });

        // Cuando el usuario elige el valor
        selectValor.on('change', function () {
          const valorSeleccionado = $(this).val();
          condicionesDice[dimension] = valorSeleccionado;

          console.log("Condiciones actuales:", condicionesDice);

          // Si hay menos de 3 dimensiones usadas, permitir añadir otra
          if (Object.keys(condicionesDice).length < 3) {
            añadirBloqueSeleccion();
          }

          // Mostrar botón si hay al menos 2 condiciones
          if (Object.keys(condicionesDice).length >= 2 && $('#realizarDice').length === 0) {
            $('#contenedorSelects').append('<button id="realizarDice" onclick="realizarDice()" class="btn btn-primary" style="margin-top:10px;">Realizar Dice</button>');
          }
        });

      } catch (error) {
        console.error("Error al obtener valores:", error);
      }
    });

    // Iniciar select2
    selectDimension.select2();
    selectValor.select2();
  }

  añadirBloqueSeleccion(); 
}

/*
// Función que crea los select para operacion dice nueva
function crearOpcionesDice2(){
   $('#contenedorSelects').empty();
  condicionesDiceLogico = [];

  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;

  // Select DIMENSIÓN
  const selectDimension = $(`
    <select id="selectDimensionDice" class="form-control select2 mb-2">
      <option value="" disabled selected>Selecciona dimensión</option>
    </select>
  `);

  for (let dimension in cubo.dimensiones) {
    selectDimension.append(`<option value="${dimension}">${dimension}</option>`);
  }

  // Contenedor valores
  const contenedorValores = $('<div id="contenedorValoresDice" class="mb-3"></div>');

  // Select operador lógico
  const selectOperador = $(`
    <select id="selectOperadorLogico" class="form-control mb-2">
      <option value="AND">AND</option>
      <option value="OR">OR</option>
    </select>
  `);

  // Botón añadir condición
  const botonAgregar = $(`<button class="btn btn-primary mb-2">➕ Añadir condición</button>`);

  // Lista condiciones añadidas
  const listaCondiciones = $('<ul id="listaCondiciones" class="list-group mb-3"></ul>');

  // Botón ejecutar
  const botonEjecutar = $(`<button class="btn btn-success">▶ Ejecutar Dice lógico</button>`);

  $('#contenedorSelects')
    .append('<label>Dimensión</label>')
    .append(selectDimension)
    .append(contenedorValores)
    .append('<label>Operador lógico</label>')
    .append(selectOperador)
    .append(botonAgregar)
    .append('<hr><strong>Condiciones añadidas:</strong>')
    .append(listaCondiciones)
    .append(botonEjecutar);

  $('#selectDimensionDice').select2();

  // Al seleccionar dimensión, obtener valores
  selectDimension.on('change', async function () {
    const dimension = $(this).val();
    const jerarquia = cubo.dimensiones[dimension].jerarquia_por_defecto;
    const niveles = cubo.dimensiones[dimension].jerarquias[jerarquia].niveles;
    const nivel = niveles[niveles.length - 1]; // Último nivel

    try {
      const response = await fetch(`http://localhost:8001/analisismultidimensional/getLevels/?nombreCubo=${nombreCubo}&nombreUser=${user}&nombreJerarquia=${jerarquia}&nombreNivel=${nivel}`);
      const data = await response.json();
      const valores = Array.from(new Set(data.valores));

      const selectValores = $(`
        <select id="selectValoresDimension" class="form-control select2" multiple>
        </select>
      `);

      valores.forEach(v => {
        selectValores.append(`<option value="${v}">${v}</option>`);
      });

      contenedorValores.empty().append('<label>Valores</label>').append(selectValores);
      $('#selectValoresDimension').select2();

    } catch (err) {
      console.error("Error al obtener valores:", err);
    }
  });

  // Añadir condición
  botonAgregar.on('click', function () {
    if (condicionesDiceLogico.length >= 3) {
      toastr.warning("No puedes añadir más de 3 condiciones");
      return;
    }

    const dimension = $('#selectDimensionDice').val();
    const valores = $('#selectValoresDimension').val();
    const operador = $('#selectOperadorLogico').val();

    if (!dimension || !valores || valores.length === 0) {
      var mensaje = i18next.t('exitoCrearCubo');
      toastr.success(mensaje);
      toastr.error("Debes seleccionar una dimensión y al menos un valor");
      return;
    }

    const condicion = {
      dimension: dimension,
      valores: valores,
      operador: operador
    };

    condicionesDiceLogico.push(condicion);

    listaCondiciones.append(`<li class="list-group-item">${operador} (${dimension} IN [${valores.join(", ")}])</li>`);
    $('#selectDimensionDice').val('').trigger('change');
    contenedorValores.empty();
  });

  // Ejecutar Dice Lógico
  botonEjecutar.on('click', function () {
    if (condicionesDiceLogico.length < 2) {
      toastr.error("Debes añadir al menos 2 condiciones");
      return;
    }

    realizarDice2();
  });
}

async function realizarDice2(){
  
  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const medida = cubo.medida;
  const operacion = cubo.tipoMedida;

  try {
    const response = await fetch(`http://localhost:8001/analisismultidimensional/dice2/?user=${user}&nombre_cubo=${nombreCubo}&medida=${medida}&operacion=${operacion}`, {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(condicionesDiceLogico)
    });

    if (!response.ok) throw new Error(`Error: ${response.status}`);
    const data = await response.json();

    console.log("Resultado Dice Lógico:", data);

    if (Array.isArray(data.resultado)) {
      crearChartDice(data.resultado, data.agrupado_por || "agrupado");
      toastr.success("Dice lógico ejecutado correctamente");
    } else if (data.resultado.total !== undefined) {
      $('#valorTotalDice').text(data.resultado.total);
      $('#resultadoDiceTotal').show();
    }

  } catch (error) {
    console.error("Error ejecutando Dice Lógico:", error);
    toastr.error("Error al ejecutar Dice Lógico");
  }
}
  */


// Función que crea los select para la operación slice
function crearOpcionesSlice() {
  console.log("Se ha seleccionado la operación de slice");
  $('#contenedorSelects').empty();

  // Nombre del cubo
  $('#contenedorSelects').append(
    '<input data-i18n="[placeholder]placeholderSliceNombreCubo" class="input-validar form-control form-control-border border-width-2" id="cubename" name="cubename" type="text" width="65%" placeholder="">' +
    '<br>'
  );

  // Select dimensión
  var divDimension = $('<div></div>');
  var selectDimension = $('<select class="form-control select2" id="selectDimensionSlice"></select><br><br>');
  selectDimension.append('<option value="" disabled selected></option>');

  for (let dimension in cubo.dimensiones) {
    selectDimension.append(new Option(dimension, dimension, false, false));
  }

  divDimension.append('<label data-i18n="labelSelectDimension">' + i18next.t('labelSelectDimension') + '</label>');
  divDimension.append(selectDimension);
  $('#contenedorSelects').append(divDimension);

  $('#selectDimensionSlice').select2({ minimumResultsForSearch: Infinity });

  // Al seleccionar dimensión, cargar jerarquías
  $('#selectDimensionSlice').on('change', function () {
     $('#diceChart').empty();
    var dimensionSeleccionada = $(this).val();
    var jerarquias = Object.keys(cubo.dimensiones[dimensionSeleccionada].jerarquias);
    var jerarquia = jerarquias[0]; // Solo usamos la jerarquía por defecto

    var niveles = cubo.dimensiones[dimensionSeleccionada].jerarquias[jerarquia].niveles;
    $('#divNivelSlice, #divValorSlice, #realizarSlice').remove(); // Reset

    // Select nivel
    var divNivel = $('<div id="divNivelSlice"></div>');
    var selectNivel = $('<select class="form-control select2" id="selectNivelSlice"></select><br><br>');
    selectNivel.append('<option value="" disabled selected></option>');

    niveles.forEach(function (nivel) {
      selectNivel.append(new Option(nivel, nivel, false, false));
    });

    divNivel.append('<label data-i18n="labelSelectNivel">' + i18next.t('labelSelectNivel') + '</label>');
    divNivel.append(selectNivel);
    $('#contenedorSelects').append(divNivel);
    $('#selectNivelSlice').select2();

    // Al seleccionar nivel, pedir valores al backend
    $('#selectNivelSlice').on('change', async function () {
      var nivelSeleccionado = $(this).val();
      var user = cubo.user;
      var nombrecubo = cubo.nombreCubo;

      try {
        //const response = await fetch(`http://localhost:8001/analisismultidimensional/getLevels/?nombreCubo=${nombrecubo}&nombreUser=${user}&nombreJerarquia=${jerarquia}&nombreNivel=${nivelSeleccionado}`);
        const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/getLevels/?nombreCubo=${nombrecubo}&nombreUser=${user}&nombreJerarquia=${jerarquia}&nombreNivel=${nivelSeleccionado}`);

        if (!response.ok) throw new Error(`Error! status: ${response.status}`);

        const data = await response.json();
        let valoresUnicos = Array.from(new Set(data.valores));

        $('#divValorSlice, #realizarSlice').remove();

        // Select valor
        var divValor = $('<div id="divValorSlice"></div>');
        var selectValor = $('<select class="form-control select2" id="selectValorSlice"></select><br><br>');
        selectValor.append('<option value="" disabled selected></option>');

        valoresUnicos.forEach(function (valor) {
          selectValor.append(new Option(valor, valor, false, false));
        });

        divValor.append('<label data-i18n="labelSelectValor">' + i18next.t('labelSelectValor') + '</label>');
        divValor.append(selectValor);
        $('#contenedorSelects').append(divValor);
        $('#selectValorSlice').select2();

        // Botón ejecutar
        $('#selectValorSlice').on('change', function () {
          $('#realizarSlice').remove();
          $('#contenedorSelects').append(`
            <button data-i18n="botonSL" id="realizarSlice" type="button" onclick="realizarSlice()"
              class="btn btn-block btn-primary" style="width: 35%; float: right;">
              ${i18next.t('botonSL')}
            </button>`);
        });

      } catch (error) {
        console.error('Error obteniendo valores:', error);
      }
    });
  });

  $('body').localize(); // Re-aplica traducción
}

function crearOpcionesSlice2(){
  console.log("Se ha seleccionado la operación de slice (por selección de dimensiones)");

  $('#contenedorSelects').empty();

  // Nombre del cubo
  // Checkboxes de dimensiones
  let checkboxGroup = $('<div id="grupoDimensionesSlice"><label>Selecciona 2 dimensiones a mantener:</label><br></div>');

  for (let dimension in cubo.dimensiones) {
    let checkbox = $(`
      <div class="form-check">
        <input class="form-check-input checkbox-dimension" type="checkbox" value="${dimension}" id="check_${dimension}">
        <label class="form-check-label" for="check_${dimension}">${dimension}</label>
      </div>
    `);
    checkboxGroup.append(checkbox);
  }

  $('#contenedorSelects').append(checkboxGroup);
  $('#contenedorSelects').on('change', 'input[type="checkbox"].dimension-slice-checkbox', function () {
  const seleccionados = $('input.dimension-slice-checkbox:checked');
  if (seleccionados.length > 2) {
    this.checked = false;
    var mensaje = i18next.t('dimensioneslimiteslice');
    toastr.warning(mensaje);
  }
});

  // Botón ejecutar
  $('#contenedorSelects').append(`
    <br>
    <button id="realizarSlice" type="button" class="btn btn-primary" onclick="realizarSlice2()">
      Realizar Slice
    </button>
  `);
}


async function realizarSlice2(){
  
  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const medida = cubo.medida;
  const operacion = "SUM";

  const dimensionesSeleccionadas = [];
  $('.checkbox-dimension:checked').each(function () {
    dimensionesSeleccionadas.push($(this).val());
  });

  if (dimensionesSeleccionadas.length !== 2) {
    var mensaje = i18next.t('dimensioneslimiterealizarslice');
    toastr.error(mensaje);
    return;
  }

  try {
    //const response = await fetch(`http://localhost:8001/analisismultidimensional/slice2/`, {
      const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/slice/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user,
        nombre_cubo: nombreCubo,
        dimensiones: dimensionesSeleccionadas,
        medida,
        operacion
      })
    });

    const resultado = await response.json();
    var mensaje = i18next.t('successlice');
    toastr.success(mensaje);
    crearChartSlice(resultado);

  } catch (err) {
    var mensaje = i18next.t('errorslice');
    toastr.error(mensaje);
  }
}


//Función que procesa la operación realizada
function procesarOperacion(operacion){

  switch(operacion){
    case "drilldown":
      
      crearOpcionesDrillDown();
      break;

    case "rollup":
      
      crearOpcionesRollUp();
      break;

    case "dice":
      
      crearOpcionesDice();
      //crearOpcionesDice2();
      break;

    case "slice":
      //crearOpcionesSlice();
      crearOpcionesSlice2();
      break;
  }
}

//Función que hace la petición a la api para realizar la operación de drill down
async function realizarDrillDown(){
  console.log("Realizando drill down");

  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const dimension = $('#selectDimensionDrill').val();
  const nivelDestino = $('#selectNivelInferior').val();
  const jerarquia = $('#selectJerarquia').val()
  const medida = cubo.medida;
  const operacion = cubo.tipoMedida;

  if(!dimension  || !nivelDestino || !nombreCubo || !user){
    var mensaje = i18next.t('errorCampos');
    toastr.error(mensaje);
    return;
  }

  console.log("Haciendo peticion a roll up");
  try {
    //const url = new URL("http://localhost:8001/analisismultidimensional/drilldown/");
    const url = new URL("http://servicios_olap:8001/analisismultidimensional/drilldown/");
    const params = {
      user: user,
      nombre_cubo: nombreCubo,
      dimension: dimension,
      medida: medida,
      nivel_destino: nivelDestino,
      operacion: operacion
    };

    Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, value));
    
    const response = await fetch(url.toString(), {
      method: 'POST'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error desconocido");
    }

    const data = await response.json();
    var mensaje = i18next.t('sucessdrilldown');
    toastr.success(mensaje);

    cubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual = nivelDestino;
    actualizarArbol();
    crearChartRollupDrillDown(data, "Drill Down");
    $('#contenedorSelects').empty();
    comprobarOperacionesDisponibles();

  } catch (error) {
    var mensaje = i18next.t('errordrilldown');
    toastr.error(mensaje);
    
  }
}


//Función que hace la petición a la api para realizar la operación de roll up
async function realizarRollUp(){

  console.log("Realizando roll up");

  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const dimension = $('#selectDimension').val();
  const nivelDestino = $('#selectNivelSuperior').val();
  const medida = cubo.medida;
  const jerarquia = $('#selectJerarquia').val()
  const operacion = cubo.tipoMedida;

  if(!dimension  || !nivelDestino || !nombreCubo || !user){
    var mensaje = i18next.t('errorCampos');
    toastr.error(mensaje);
    return;
  }

  console.log("Haciendo peticion a roll up");
  try {
    //const url = new URL("http://localhost:8001/analisismultidimensional/rollup/");
    const url = new URL("http://servicios_olap:8001/analisismultidimensional/rollup/");
    const params = {
      user: user,
      nombre_cubo: nombreCubo,
      dimension: dimension,
      medida: medida,
      operacion: operacion,
      nivel_destino: nivelDestino
    };

    Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, value));
    
    const response = await fetch(url.toString(), {
      method: 'POST'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error desconocido");
    }

    const data = await response.json();
    var mensaje = i18next.t('sucessrollup');
    toastr.success(mensaje)
    
    cubo.dimensiones[dimension].jerarquias[jerarquia].nivel_actual = nivelDestino;
    actualizarArbol();
    crearChartRollupDrillDown(data, "Roll Up");
    $('#contenedorSelects').empty();
    comprobarOperacionesDisponibles();

  } catch (error) {
    var mensaje = i18next.t('errorrollup');
    toastr.error(mensaje);
  }
}


//Función que hace la petición a la api para realizar la operación de dice
async function realizarDice(){
  console.log("Realizando dice");
  if (Object.keys(condicionesDice).length < 2) {
    var mensaje = i18next.t('errorcamposdice');
    toastr.error(mensaje);
    return;
  }
 
  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const medida = cubo.medida;
  const operacion = cubo.tipoMedida;

  try {
    //const response = await fetch(`http://localhost:8001/analisismultidimensional/dice/?user=${user}&nombre_cubo=${nombreCubo}&medida=${medida}&operacion=${operacion}`, {
      const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/dice/?user=${user}&nombre_cubo=${nombreCubo}&medida=${medida}&operacion=${operacion}`, {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(condicionesDice)
    });

    if (!response.ok) {
      throw new Error(`Error al hacer la petición: ${response.status}`);
    }

    const data = await response.json();
    console.log("Resultado del Dice:", data);


    if (Array.isArray(data.resultado)) {
      var mensaje = i18next.t('successdice');
      toastr.success(mensaje);
      
      crearChartDice(data.resultado, data.agrupado_por);
      $('#contenedorSelects').empty();
      comprobarOperacionesDisponibles();
      
    } else {
      var mensaje = i18next.t('successdice');
      toastr.success(mensaje);
      
      crearChartDice(data.resultado, data.agrupado_por);
      $('#contenedorSelects').empty();
      comprobarOperacionesDisponibles();
      
    }

  } catch (error) {
      var mensaje = i18next.t('errordice');
      toastr.error(mensaje);
  
  }
}

/*
//Función que hace la petición a la api para realizar la operación de slice
async function realizarSlice(){

  console.log("Realizando slice");

  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;

  const dimension = $('#selectDimensionSlice').val();
  const nivel = $('#selectNivelSlice').val();
  const valor = $('#selectValorSlice').val();
  const medida = cubo.medida;
  const operacion =  cubo.tipoMedida;

  if (!dimension || !nivel || !valor || !medida || !operacion) {
    
    toastr.error("Faltan datos para realizar el slice.");
    return;
  }

   try {
    const response = await fetch(`http://localhost:8001/analisismultidimensional/slice/?user=${user}&nombre_cubo=${nombreCubo}&dimension=${dimension}&nivel=${nivel}&valor=${encodeURIComponent(valor)}&medida=${medida}&operacion=${operacion}`, {
      method: "POST"
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Error en la operación slice");
    }

    const resultado = await response.json();
    console.log("Resultado del slice:", resultado);
    toastr.success("Slice realizado correctamente");
    crearChartSlice(resultado);
    $('#contenedorSelects').empty();
    comprobarOperacionesDisponibles();
    
  } catch (error) {
    console.error("Error al realizar slice:", error);
    toastr.error("Error al realizar slice");
  }
}
  */



var tree = $('#tree');

//Comprobamos si se puede realizar la operación drilldown
//Para ello, miramos si en cada dimension el nivel actual no está en la posición mas especifica (la ultima)
//Para cada dimensión comprobamos que haya más de una jerarquía
function comprobarDrillDown() {
  
  let disponible = false;
 
  for (let dimension in cubo.dimensiones) {
    let jerarquiaDefecto = cubo.dimensiones[dimension].jerarquia_por_defecto;
    let niveles = cubo.dimensiones[dimension].jerarquias[jerarquiaDefecto].niveles;
    let nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquiaDefecto].nivel_actual;

    let idxActual = niveles.indexOf(nivelActual);

    // Si no estamos en el nivel más específico (última posición), podemos hacer drill-down
    if (idxActual < niveles.length - 1) {
      disponible = true;
      dimensionesDisponiblesDD[dimension] = {
        niveles: niveles,
        actual: nivelActual,
        posible_inferior: niveles[idxActual + 1]
      };
    }
  }

  console.log("Dimensiones disponibles para drill-down: " + dimensionesDisponiblesDD);
  return disponible;
  
}

//Comprobamos si se puede realizar la operación rollup
//Para ello, miramos si en cada dimension el nivel actual no está en la posición 0 (el más general)
//Para cada dimensión comprobamos que haya más de un nivel
function comprobarRollup(){

  console.log("Comprobando roll-up");
  let disponible = false;
  
  for (let dimension in cubo.dimensiones) {
    let jerarquiaDefecto = cubo.dimensiones[dimension].jerarquia_por_defecto;
    let niveles = cubo.dimensiones[dimension].jerarquias[jerarquiaDefecto].niveles;
    let nivelActual = cubo.dimensiones[dimension].jerarquias[jerarquiaDefecto].nivel_actual;

    let idxActual = niveles.indexOf(nivelActual);

    // Si no estamos en el nivel más general (posición 0), podemos hacer roll-up
    if (idxActual > 0) {
      disponible = true;
      dimensionesDisponiblesRU[dimension] = {
        niveles: niveles,
        actual: nivelActual,
        posible_superior: niveles[idxActual - 1]
      };
    }
  }

  console.log("Dimensiones disponibles para rollup: " + dimensionesDisponiblesRU);
  return disponible;
}
   

//Comprobamos si se puede realizar la operación Slice
//Para ello, el cubo tiene que tener al menos una dimensión
function comprobarSlice() {
  console.log("Comprobando slice");

  return Object.keys(cubo.dimensiones).length > 0;
}

//Comprobamos si se puede realizar la operación dice
//Para ello, el cubo tiene que tener al menos dos dimensiones
function comprobarDice(){
  console.log("Comprobando dice");
  var disponible = false;

  //Comprobamos que haya al menos dos dimensiones en el cubo
  const dims = Object.keys(cubo.dimensiones);
  if (dims.length >= 2) {
    dimensionesDice.push(...dims);
    disponible =  true;
  }

  return disponible;

}


function comprobarOperacionesDisponibles(){
  console.log("Dentro de comprobando");

  if(!comprobarDrillDown()){
    $('#operaciones').find('option[value="drilldown"]').prop('disabled', true);
  }
  
  if(!comprobarRollup()){
    $('#operaciones').find('option[value="rollup"]').prop('disabled', true);
  }

  if(!comprobarSlice()){
    $('#operaciones').find('option[value="slice"]').prop('disabled', true);
  }

  if(!comprobarDice()){
    $('#operaciones').find('option[value="dice"]').prop('disabled', true);
  }

}

var inputs;

$(document).ready(async function(){

  //Validación de los inputs para que no se introduzcan caracteres no deseados
  //inputs = document.querySelectorAll('.input-validar');
  $('#dimensionesSlice').select2();

    diceChart = null;

    //Recuperamos el valor del cubo
    var parametrosURL = new URLSearchParams(window.location.search);
    var dataCuboEncoded = parametrosURL.get('cubo');
    var dataCuboDecoded = atob(dataCuboEncoded);
    cuboPeticion = JSON.parse(dataCuboDecoded);

    console.log("Dimensiones de cubopeticion: ", cuboPeticion.dimensiones);

    user = cuboPeticion.user;
    nombrecubo = cuboPeticion.nombreCubo
    console.log("user: ", user);
    console.log("nombrecubo: ", nombrecubo);

    //Peticion
    try {
      //const response = await fetch(`http://localhost:8001/analisismultidimensional/getCube/?user=${user}&nombre_cubo=${nombrecubo}`);
      const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/getCube/?user=${user}&nombre_cubo=${nombrecubo}`);
      if (!response.ok){
        throw new Error(`Error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Respuesta del servidor: ", data);
      cubo = data;
      console.log("Nuevo cubo: ", cubo)
      console.log("Dimensiones del nuevo cubo; ", cubo.dimensiones);
    } catch (error) {
        console.error('Error: ', error)
    }

    /*
    fetch(`http://localhost:8001/analisismultidimensional/getCube/?user=${user}&nombre_cubo=${nombrecubo}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(response.statusText);
        }
        return response.json();
      })
      .then(data => {
        console.log("Respuesta del servidor: ", data);
        cubo = data;
        console.log("Nuevo cubo: ", cubo)
        console.log("Dimensiones del nuevo cubo; ", cubo.dimensiones);
      })
      .catch(error => {
        console.error('Error:', error);
      })
        */

    //getCubo(cuboPeticion.user, cuboPeticion.nombreCubo)
    inicializarTraducciones();

    console.log("Despues de la peticion, datos del cubo:", cubo)

    //Comprobamos las operaciones que se pueden aplicar sobre el cubo
    //Las que no se puedan realizar, no se podrán seleccionar
    comprobarOperacionesDisponibles();

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
        var match = contenidoNodo.match(/<span class="titulo-nivel">(.*?)<\/span>/);
        var valorNodo = "";
        if (match && match[1]){
          valorNodo = match[1];
        } else {
          
          valorNodo = nodo.title;
        }
        var valor = valorNodo || "";
        
        // Actualizar el contenido del span con la información del nodo activado
        console.log("Tipo del nodo: " , tipoNodo);
        console.log("Nombre del nodo: " , contenidoNodo);
        //$("#infonodo").text("Tipo de nodo: " + tipoNodo);
        //$("#infovalor").text("Nombre: " + contenidoNodo);
        $("#infonodo").text(i18next.t('tipoNodo', {tipo: tipoNodo}));
        $("#infovalor").text(i18next.t('nombreNodo', {valor: valor}));
        //$("#info").text("Contenido: " + contenidoNodo);
       
      },
      renderTitle: function(event, data) {
        data.node.span.innerHTML = data.node.title;
      }
    });
  
    tree = $.ui.fancytree.getTree("#tree");
  
    $("#descripcion").text(i18next.t('descripcionCubo'));
    $("#nombrecubo").text(i18next.t('nombreCubo'));
    $("#medidaCubo").text(i18next.t('medidaCubo'));


    /*
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
      */
    actualizarArbol();
    imprimirArbol();
    
    

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

function crearChartDice(resultado, agrupadopor){
  $('#contenedorGraficosResumen').empty();
  $('#resultadoDiceTotal').hide();
  $('#botonOcultarGrafico').remove();

  

  if(Array.isArray(resultado)) {
    console.log("Dentro de crear el chat de dice");
    
    const labels = resultado.map(item => item.nivel);
    const datos = resultado.map(item => item.valor);

    console.log("Estos son los labels: " + labels);
    console.log("Estos son los datos: " + datos);
    
    var canvas = document.getElementById('diceChart');

    const ctx = canvas.getContext('2d');

    if (canvas.chartInstance) {
      canvas.chartInstance.destroy();
    }

    // Se muestra botón para ocultar los datos
    if (!$('#botonOcultarGrafico').length) {
      const boton = $(`
        <button id="botonOcultarGrafico" class="btn btn-block btn-dark"
        style="width: 70px; height: 70px; padding: 0; font-weight: bold; font-size: 28px; line-height: 1; text-align: center;">
          &times;
        </button>
      `);

      $('#botonOcultarGraficoContainer').append(boton);

      $('#botonOcultarGrafico').on('click', function () {
        $('#diceChart').hide(); // Oculta los gráficos
        $(this).remove(); // Elimina el botón
      });
    }

    canvas.chartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Valores agrupados por ' + agrupadopor,
          data: datos,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Resultado de operación DICE'
          }
        },
        scales: {
          yAxes: [{
            ticks: {
                beginAtZero: true
            }
          }]
        }
      }
    });
  } 
   else if (resultado.total !== undefined) {
    
  if (resultado.total === null) {
    var mensaje = i18next.t('errorchardice');
    toastr.error(mensaje);
    $('#resultadoDiceTotal').hide();
  } else {
    const labels = [agrupadopor];
    const valor = [resultado.total];

    
    var canvas = document.getElementById('diceChart');
    const ctx = canvas.getContext('2d');

    if (canvas.chartInstance) {
      canvas.chartInstance.destroy();
    }

    // Se muestra botón para ocultar los datos
    if (!$('#botonOcultarGrafico').length) {
      const boton = $(`
        <button id="botonOcultarGrafico" class="btn btn-block btn-dark"
        style="width: 70px; height: 70px; padding: 0; font-weight: bold; font-size: 28px; line-height: 1; text-align: center;">
          &times;
        </button>
      `);

      $('#botonOcultarGraficoContainer').append(boton);

      $('#botonOcultarGrafico').on('click', function () {
        $('#diceChart').hide(); // Oculta los gráficos
        $(this).remove(); // Elimina el botón
      });
    }

    canvas.chartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Resultado total',
          data: valor,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Resultado de operación DICE (valor único)'
          }
        },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
    }
  }
}

function crearChartRollupDrillDown(resultado, operacion){
   $('#contenedorGraficosResumen').empty();
   //$('#diceChart').empty();
    $('#botonOcultarGrafico').remove();
   console.log("Dentro de crear el chat de ru/dd");

  console.log("Resultado: " + resultado);

    const labels = resultado.datos.map(item => item.nivel);
    const valores = resultado.datos.map(item => item.valor);

    console.log("Estos son los labels: " + labels);
    console.log("Estos son los valores: " + valores);
    
    var canvas = document.getElementById('diceChart');

    const ctx = canvas.getContext('2d');

    if (canvas.chartInstance) {
      canvas.chartInstance.destroy();
    }

    // Se muestra botón para ocultar los datos
    if (!$('#botonOcultarGrafico').length) {
      const boton = $(`
        <button id="botonOcultarGrafico" class="btn btn-block btn-dark"
        style="width: 70px; height: 70px; padding: 0; font-weight: bold; font-size: 28px; line-height: 1; text-align: center;">
          &times;
        </button>
      `);

      $('#botonOcultarGraficoContainer').append(boton);

      $('#botonOcultarGrafico').on('click', function () {
        $('#diceChart').hide(); // Oculta los gráficos
        $(this).remove(); // Elimina el botón
      });
    }

    canvas.chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: `${resultado.operacion} (${resultado.dimension} agrupado por ${resultado.agrupado_por} usando operación de agregación ${resultado.tipo_agregacion})`,
        data: valores,
        backgroundColor: 'rgba(153, 102, 255, 0.6)'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: `Resultado de ${operacion.toUpperCase()}`
        }
      },
      scales: {
        yAxes: [{
          ticks: {
              beginAtZero: true,
          }
        }]
      }
    }
  });
}

function crearChartSlice(resultado){
  $('#contenedorGraficosResumen').empty();
  $('#botonOcultarGrafico').remove();
  
  const resultados = resultado.datos;
  if (!Array.isArray(resultados) || resultados.length === 0) {
    var mensaje = i18next.t('errorcharslice');
    toastr.error(mensaje);
    return;
  }

  var canvas = document.getElementById('diceChart');

  const ctx = canvas.getContext('2d');

  if (canvas.chartInstance) {
    canvas.chartInstance.destroy();
  }

  // Se muestra botón para ocultar los datos
    if (!$('#botonOcultarGrafico').length) {
      const boton = $(`
        <button id="botonOcultarGrafico" class="btn btn-block btn-dark"
        style="width: 70px; height: 70px; padding: 0; font-weight: bold; font-size: 28px; line-height: 1; text-align: center;">
          &times;
        </button>
      `);

      $('#botonOcultarGraficoContainer').append(boton);

      $('#botonOcultarGrafico').on('click', function () {
        $('#diceChart').hide(); // Oculta los gráficos
        $(this).remove(); // Elimina el botón
      });
    }

  // Detectar las columnas (excepto "total")
  const keys = Object.keys(resultados[0]).filter(k => k !== "total");

  // Si hay más de una dimensión, combinarlas en un label
  const labels = resultados.map(r => keys.map(k => r[k]).join(" - "));
  const valores = resultados.map(r => r.total);

  canvas.chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: `Slice sobre dimensiones: ${resultado.dimensiones_mantenidas.join(" y ")}`,
        data: valores,
        backgroundColor: 'rgba(255, 159, 64, 0.6)'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Resultado de Slice'
        }
      },
      scales: {
          yAxes: [{
            ticks: {
                beginAtZero: true,
            }
          }]
      }
    }
  });

}

let charts = {};

//Funcion para crear charts individuales
function crearChartDimension(canvasId, titulo, datos) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  const canvas = document.getElementById(canvasId);

  if (canvas.chartInstance) {
    canvas.chartInstance.destroy();
  }

  // Destruir gráfico anterior si ya existe
  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  console.log("Esto son los datos que vienen: " + datos);

  const labels = datos.map(item => item.nivel);
  const valores = datos.map(item => item.valor);

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: titulo,
        data: valores,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true,
          }
        }]
      },
      plugins: {
        title: {
          display: true,
          text: titulo
        }
      }
    }
  });

  charts[canvasId] = chart;
}

//Función para mostrar los datos del cubo segun los niveles actuales
async function mostrarResumenCubo() {
  const user = cubo.user;
  const nombreCubo = cubo.nombreCubo;
  const medida = cubo.medida;
  const operacion = "SUM";

  try {
    //const response = await fetch(`http://localhost:8001/analisismultidimensional/getDatosCubo/?user=${user}&nombre_cubo=${nombreCubo}&medida=${medida}&operacion=${operacion}`, {
    const response = await fetch(`http://servicios_olap:8001/analisismultidimensional/getDatosCubo/?user=${user}&nombre_cubo=${nombreCubo}&medida=${medida}&operacion=${operacion}`, {

      method: 'POST'
    });

    if (!response.ok) throw new Error("Error al obtener resumen del cubo");

    const data = await response.json();
    console.log("Resumen del cubo:", data);

    $('#contenedorGraficosResumen').show();
    $('#botonOcultarDatos').remove();
   
    $('#contenedorGraficosResumen').empty();
      charts = {};

    for(const dimension in data.datos) {
      const idCanvas = "chart_" + dimension;

    $('#contenedorGraficosResumen').append(`
      <div class="grafico-caja">
        <canvas id="${idCanvas}" height="300"></canvas>
      </div>
    `);

      const titulo = cubo.medida + " agrupado por " + data.dimension_niveles_actuales[dimension];

      
      console.log("Datos de la dimension: " + data.datos[dimension])
      crearChartDimension(idCanvas, titulo, data.datos[dimension]);
    }

    // Se muestra botón para ocultar los datos
    if (!$('#botonOcultarDatos').length) {
    const boton = $(`
      <button id="botonOcultarDatos" class="btn btn-block btn-dark"
      style="width: 70px; height: 70px; padding: 0; font-weight: bold; font-size: 28px; line-height: 1; text-align: center;">
         &times;
      </button>
    `);

    $('#botonOcultarDatosContainer').append(boton);

    $('#botonOcultarDatos').on('click', function () {
      $('#contenedorGraficosResumen').hide(); // Oculta los gráficos
      $(this).remove(); // Elimina el botón
    });
  }
    var mensaje = i18next.t('successresumen');
    toastr.success(mensaje);

  } catch (err) {
    var mensaje = i18next.t('errorresumen');
    toastr.error(mensaje);
  }
}

  
 function actualizarArbol(){

  console.log("Dento de actualizar arbol");
    // Borramos el árbol actual
  var tree = $.ui.fancytree.getTree("#tree");

  if (!tree) {
  console.log("No se pudo obtener el árbol (#tree no está inicializado aún)");
  return;
  }

  var rootNode = tree.getRootNode();

  if (!rootNode) {
  console.log("El nodo raíz del árbol no está disponible.");
  return;
}

  tree.getRootNode().removeChildren();

  // Iteramos por las dimensiones
  Object.keys(cubo.dimensiones).forEach(function(dimension) {
    // Creamos nodo para la dimensión
    var nodoDimension = rootNode.addChildren({
      title: dimension,
      tipo: "Dimension",
      extraClasses: "fancytree-dimension",
      icon: "icono-dimension",
    });

    tree.expandAll();  

    var jerarquias = cubo.dimensiones[dimension].jerarquias;
    var jerarquiaNombre = Object.keys(jerarquias)[0]; // Solo hay una
    var jerarquiaPorDefecto = cubo.dimensiones[dimension].jerarquia_por_defecto;
    console.log("Jerarquia nombre: " + jerarquiaNombre);
    nivelActual = jerarquias[jerarquiaNombre].nivel_actual;
    console.log("Nivel actual: ", nivelActual)
  
    //var niveles = jerarquias[jerarquia].niveles || [];

    //Si no hay jerarquias todavia, sale de la función
    if (!jerarquiaNombre){
      return;
    }

    // Iteramos sobre todas las jerarquías 
    console.log("Antes de iterar sobre las jerarquias")
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
      /*
      // Obtenemos y recorremos los niveles de esta jerarquía
      niveles.forEach(function(nivel) {
        nodoJerarquia.addChildren({
          title: nivel,
          tipo: nivel === nivelActual ? "Nivel actual" : "Nivel",
          extraClasses: nivel === nivelActual 
            ? "fancytree-nivel-actual"
            : "fancytree-nivel",
          icon: "icono-nivel",
        });
      });*/
      niveles.forEach(function(nivel) {
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
  
function imprimirArbol(){

  console.log(cubo.nombreCubo);
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

  
  