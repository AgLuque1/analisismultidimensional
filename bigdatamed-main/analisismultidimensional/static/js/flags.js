var language = 'es';
    const flagsElement = document.getElementById("flags");
    const inputsToChange = document.querySelectorAll("input[data-placeholder]");
    const textsToChange = document.querySelectorAll("[data-section");

    const changeLanguage = async language=>{
        const requestJson = await fetch(`../static/languages/${language}.json`);
        const texts = await requestJson.json();

        for(const textToChange of textsToChange){
            
            const section = textToChange.dataset.section;
           
            const value = textToChange.dataset.value;
          
            textToChange.innerHTML = texts[section][value];
        }

        inputsToChange.forEach((inputToChange) => {
            
            const placeholderKey = inputToChange.dataset.placeholder;
            
            const translatedPlaceholder = texts.placeholders[placeholderKey];
            // Actualiza el placeholder del input
            
            inputToChange.placeholder = translatedPlaceholder;
          });

         
    }


    //Función que inicializa las traducciones para los elementos dinámicos
function inicializarTraducciones(){
    //Configuración de biblioteca para traducciones
    i18next.use(i18nextBrowserLanguageDetector).init({
     fallbackLng: 'es', // Idioma por defecto
     debug: true,
     resources: {
       en: {
         translation: {
            "botonAyuda": "Help",
            "botonLogout": "Log out",
            "labelSelectDimension": "Select dimension",
            "labelSelectJerarquia": "Select hiearchy",
            "labelSelectNivel": "Select level",
            "labelSelectJerarquia": "Select hierarchy",
            "labelSelectValor": "Select value",
            "placeholderSliceNombreCubo": "Enter new cube name",
            "descripcionCubo": "Description: " + cubo.descripcion,
            "nombreCubo": "Cube name: " + cubo.nombreCubo,
            "medidaCubo": "Aggregation measure: " + cubo.tipoMedida,
            "tipoNodo": "Node type: {{tipo}}",
            "nombreNodo": "Node value: {{valor}}",
            "botonRU": "Apply ROLL UP operation",
            "botonDD": "Apply DRILL DOWN operation",
            "botonSL": "Apply SLICE operation",
            "botonDC": "Apply DICE operation",
            "botonAgregarValor": "Add value",
            "errorCampos": "Please fill in all fields",
            "sinSeleccionar": "Not selected",
            "botonBorrarCubo": "Delete cube",
             "botonVerDatosCubo": "View Cube Data",
            "tituloSidebar": "Multidimensional Analysis",
            "crearCuboSidebar": "Create cube",
            "nuevoCuboSidebar": "New Cube",
            "existenteCuboSidebar": "From an existing cube",
            "misCubosSidebar": "Explore my cubes",
            "visualizacionSidebar": "Data visualization",
            "operacionesCard": "OLAP Operations",
            "vistaCard": "Cube view",
            "operacionesSelect": "Select operation",
            "crearCuboCard": "Create cube",
            "definirCard": "Cube definition",
            "nombreLabel": "Name",
            "placeholderNombreCubo": "Enter cube name",
            "descripcionLabel": "Description",
            "bdLabel": "Database",
            "spanBd": "Select the database to use",
            "labelExp": "Experimentations",
            "spanExp": "Select experimentation",
            "labelNiveles": "Keys",
            "spanNiveles": "Selects the keys to be used from the experimentation",
            "ignorarFilas": "Ignore rows with null values",
            "estructuraCard": "Structure definition",
            "dimensionesLabel": "Dimensions",
            "placeholderDimensiones": "Enter dimension name",
            "botonCrearDim": "Add dimension",
            "spanDimensiones": "Select dimension",
            "modalDimension": "Are you sure you want to delete this dimension? This action cannot be undone",
            "botonModalCerrar": "Close",
            "botonModalSeguro": "Delete",
            "labelJerarquias": "Hierarchies",
            "placeholderJerarquias": "Enter hierarchy name",
            "botonCrearJer": "Add hierarchy",
            "spanJerarquias": "Select hierarchy",
            "modalJerarquias": "Are you sure you want to delete this hierarchy? This action cannot be undone",
            "labelColumnas": "Levels",
            "placeholderNiveles": "Enter level name",
            "botonCrearNiv": "Add level",
            "spanNiveles": "Select key",
            "modalNivel": "Are you sure you want to delete this level? This action cannot be undone",
            "botonOrden": "Apply order",
            "tituloDefecto": "Select default levels",
            "labelOrden": "Drag to set the order of leves (top more general, bottom more specific)",
            "medidaCard": "Measure definition",
            "labelMedida": "Measure",
            "dimensioneslimiteslice": "You can only select two dimensions to make a Slice.",
            "dimensioneslimiterealizarslice": "You must select exactly 2 dimensions.",
            "errorslice": "Error performing slice",
            "successlice": "Slice successfully performed",
            "sucessdrilldown": "Drill down successfully performed",
            "errordrilldown": "Error performing drill down",
            "sucessrollup": "Roll up successfully performed",
            "errorrollup": "Error performing roll up",
            "errorcamposdice": "You must select at least two dimensions with values",
            "errorchardice": "No data matching the selected conditions were found",
            "successdice": "Dice successfully performed",
            "errordice": "Error performing dice",
            "errorcharslice": "There is no data to display in the slice chart",
            "successresumen": "Summary correctly generated",
            "errorresumen": "Cube summary could not be displayed",
            "placeholderMedida": "Enter measure name",
            "labelAgregacion": "Aggregation measure",
            "spanAgregacion": "Select a measurement type",
            "botonGuardar": "Save configuration",
            "errorDimensionSeleccionada": "No dimension selected",
            "errorJerarquiaSeleccionada": "No No hierarchy selected",
            "errorNivelSeleccionado": "No level selected",
            "errorCaracter": "Enter valid character",
            "exitoCrearDimension": "Dimension added",
            "yaExisteDim": "There is already a dimension with that name",
            "introduceDim": "Enter a dimension name",
            "exitoCrearJerarquia": "Hiearchy added",
            "yaExisteJer": "There is already a hierarchy with that name",
            "introduceJer": "Enter a hierarchy name and select a dimension",
            "seleccionaJer": "Select hierarchy",
            "yaExisteNiv": "The level has already been added",
            "exitoCrearNivel": "Level added",
            "eliminarDim": "Dimension deleted",
            "eliminarJer": "Hierarchy deleted",
            "eliminarNiv": "Level deleted",
            "noPerteneceNiv": "The level does not belong to the cube",
            "dimensionSinCompletar": "Dimension {{nombre}} not completed",
            "jerarquiaSinCompletar": "Hierarchy {{nombre}} not completed",
            "exitoCrearCubo": "Cube created successfully",
            "yaExisteCubo": "There is already a cube with that name",
            "columnaNombre": "Cube name",
            "columnaExp": "Experimentation name",
            "columnaFecha": "Date of creation",
            "columnaDesc": "Description",
            "exitoDD": "Drill Down operation applied properly",
            "errorDD": "Error applying Drill Down operation",
            "exitoRU": "Roll Up operation applied properly",
            "errorRU": "Error applying Roll Up operation",
            "exitoSL": "Slice operation applied properly",
            "errorSL": "Error applying Slice operation",
            "exitoDC": "Dice operation applied properly",
            "errorDC": "Error applying Dice operation",
            "errorValorAñadidoSlice": "Value has already been added to this dimension",
            "exitoValorAñadidoSlice": "Value has been added to the dimension",
            "dimensionesQuitarSlice": "Select the dimensions you want to delete",
            "limiteSlice": "You can select up to {{num}} dimensions."
           
         }
       },
       es: {
         translation: {
            "botonAyuda": "Ayuda",
            "botonLogout": "Cerrar sesión",
            "labelSelectDimension": "Selecciona la dimensión",
            "labelSelectJerarquia": "Selecciona la jerarquía",
            "labelSelectNivel": "Selecciona un nivel",
            "labelSelectJerarquia": "Selecciona una jerarquia",
            "labelSelectValor": "Selecciona un valor",
            "placeholderSliceNombreCubo": "Introduce nombre del nuevo cubo",
            "descripcionCubo": "Descripción: " + cubo.descripcion,
            "nombreCubo": "Nombre del cubo: " + cubo.nombreCubo,
            "medidaCubo": "Medida de agregación: " + cubo.tipoMedida,
            "tipoNodo": "Tipo nodo: {{tipo}}",
            "nombreNodo": "Valor nodo: {{valor}}",
            "botonRU": "Aplicar operación ROLL UP",
            "botonDD": "Aplicar operación DRILL DOWN",
            "botonSL": "Aplicar operación SLICE",
            "botonDC": "Aplicar operación DICE",
            "botonAgregarValor": "Agregar valor",
            "errorCampos": "Por favor rellena todos los campos",
            "sinSeleccionar": "Sin seleccionar",
            "botonBorrarCubo": "Eliminar cubo",
            "botonVerDatosCubo": "Ver datos del cubo",
            "tituloSidebar": "Análisis Multidimensional",
            "crearCuboSidebar": "Crear cubo",
            "nuevoCuboSidebar": "Cubo nuevo",
            "existenteCuboSidebar": "A partir de un cubo existente",
            "misCubosSidebar": "Ver mis cubos",
            "visualizacionSidebar": "Visualización de datos",
            "operacionesCard": "Operaciones OLAP",
            "vistaCard": "Vista Cubo",
            "operacionesSelect": "Selecciona una operación",
            "crearCuboCard": "Crear cubo",
            "definirCard": "Definir cubo",
            "nombreLabel": "Nombre",
            "placeholderNombreCubo": "Introduce nombre del cubo",
            "descripcionLabel": "Descripción",
            "bdLabel": "Base de datos",
            "spanBd": "Selecciona la base de datos a utilizar",
            "labelExp": "Experimentaciones",
            "spanExp": "Selecciona la experimentación",
            "labelNiveles": "Claves",
            "spanNiveles": "Selecciona las claves a utilizar de la experimentación",
            "ignorarFilas": "Ignorar filas con valores nulos",
            "estructuraCard": "Definir estructura",
            "dimensionesLabel": "Dimensiones",
            "placeholderDimensiones": "Introduce nombre de dimensión",
            "botonCrearDim": "Añadir dimensión",
            "spanDimensiones": "Selecciona una dimensión",
            "modalDimension": "¿Estás seguro de borrar esta dimension? Esta acción no se puede deshacer",
            "botonModalCerrar": "Cerrar",
            "botonModalSeguro": "Eliminar",
            "labelJerarquias": "Jerarquías",
            "placeholderJerarquias": "Introduce nombre de jerarquía",
            "botonCrearJer": "Añadir jerarquía",
            "spanJerarquias": "Selecciona una jerarquía",
            "modalJerarquias": "¿Estás seguro de borrar esta jerarquia? Esta acción no se puede deshacer",
            "labelColumnas": "Niveles",
            "placeholderNiveles": "Introduce nombre de nivel",
            "botonCrearNiv": "Añadir nivel",
            "spanNiveles": "Selecciona una clave",
            "modalNivel": "¿Estás seguro de borrar este nivel? Esta acción no se puede deshacer",
            "botonOrden": "Aplicar orden",
            "tituloDefecto": "Seleccionar nivel por defecto",
            "labelOrden": "Arrastra para establecer el orden de niveles (arriba más general, abajo más específico)",
            "medidaCard": "Definir medida",
            "labelMedida": "Medida",
            "dimensioneslimiteslice": "Solo puedes seleccionar dos dimensiones para realizar un Slice",
            "dimensioneslimiterealizarslice": "Debes seleccionar exactamente 2 dimensiones",
            "errorslice": "Error al realizar slice",
            "successlice": "Slice realizado correctamente",
            "sucessdrilldown": "Drill down realizado correctamente",
            "errordrilldown": "Error al realizar drill down",
            "sucessrollup": "Roll up realizado correctamente",
            "errorrollup": "Error al realizar roll up",
            "errorcamposdice": "Debes seleccionar al menos dos dimensiones con valores",
            "errorcharslice": "No hay datos para mostrar en el gráfico Slice",
            "successdice": "Dice realizado correctamente",
            "errordice": "Error al realizar dice",
            "errorchardice": "No se encontraron datos que coincidan con las condiciones seleccionadas",
            "successresumen": "Resumen generado correctamente",
            "errorresumen": "No se pudo mostrar el resumen del cubo",
            "placeholderMedida": "Introduce nombre de medida",
            "labelAgregacion": "Medida de agregación",
            "spanAgregacion": "Selecciona un tipo de medida",
            "botonGuardar": "Guardar configuración",
            "errorDimensionSeleccionada": "No hay dimensión seleccionada",
            "errorJerarquiaSeleccionada": "No hay jerarquía seleccionada",
            "errorNivelSeleccionado": "No hay nivel seleccionado",
            "errorCaracter": "Introduce carácter válido",
            "exitoCrearDimension": "Dimensión añadida",
            "yaExisteDim": "Ya existe una dimensión con ese nombre",
            "introduceDim": "Introduce un nombre de dimensión",
            "exitoCrearJerarquia": "Jerarquía añadida",
            "yaExisteJer": "Ya existe una jerarquía con ese nombre",
            "introduceJer": "Introduce un nombre de jerarquía y selecciona una dimensión",
            "seleccionaJer": "Selecciona una jerarquía",
            "yaExisteNiv": "El nivel ya se ha añadido",
            "exitoCrearNivel": "Nivel añadido",
            "eliminarDim": "Dimensión eliminada",
            "eliminarJer": "Jerarquía eliminada",
            "eliminarNiv": "Nivel eliminado",
            "noPerteneceNiv": "El nivel no pertenece al cubo",
            "dimensionSinCompletar": "Dimensión {{nombre}} sin completar",
            "jerarquiaSinCompletar": "Jerarquía {{nombre}} sin completar",
            "exitoCrearCubo": "Cubo creado correctamente",
            "yaExisteCubo": "Ya existe un cubo con ese nombre",
            "columnaNombre": "Nombre del cubo",
            "columnaExp": "Nombre de la experimentación",
            "columnaFecha": "Fecha de creación",
            "columnaDesc": "Descripción",
            "exitoDD": "Operación Drill Down aplicada correctamente",
            "errorDD": "Error al aplicar la operación Drill Down",
            "exitoRU": "Operación Roll Up aplicada correctamente",
            "errorRU": "Error al aplicar la operación Roll Up",
            "exitoSL": "Operación Slice aplicada correctamente",
            "errorSL": "Error al aplicar la operación Slice",
            "exitoDC": "Operación Dice aplicada correctamente",
            "errorDC": "Error al aplicar la operación Dice",
            "errorValorAñadidoSlice": "Ya se ha añadido un valor a esa dimensión",
            "exitoValorAñadidoSlice": "El valor se ha añadido a la dimensión",
            "dimensionesQuitarSlice": "Selecciona las dimensiones que deseas eliminar",
            "limiteSlice": "Puedes seleccionar hasta {{num}} dimensiones"
           
         }
       }
     }
   }, function(err, t) {
     // Inicializa la integración de jQuery
     jqueryI18next.init(i18next, $);
     
     // Traduce el contenido estático inicial
     $('body').localize();
   });
 
    //Evento para cambiar el idioma
    const flagsElement = document.getElementById("flags");
 
    flagsElement.addEventListener("click", (e) => {
      var nuevoIdioma = e.target.parentElement.dataset.value;
      console.log("nuevoIdioma: ", nuevoIdioma);
      i18next.changeLanguage(nuevoIdioma, function(err, t) {
        if (err) return console.log('Error cambiando idioma:', err);
  
        // Traduce el contenido de la página
        $('body').localize();
      });
      //language = e.target.parentElement.dataset.value;
      //console.log(e.target.parentElement.dataset.value);
      
      //changeLanguage(e.target.parentElement.dataset.language);
    });
 }
 
   
 /*
    flagsElement.addEventListener("click", (e) => {
        language = e.target.parentElement.dataset.value;
        console.log(e.target.parentElement.dataset.value);
        
        changeLanguage(e.target.parentElement.dataset.language);
    });
*/


