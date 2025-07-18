$(function () {

   /**
    * Default DataTable when user load the page first time
    * Load Data the most frecuence diagnostic 
    */

   // $("#first-data").dataTable({
   //    paging:true,
   //    deferRender:true,
   //    ajax: function (data, callback, settings) {
   //       $.ajax({
   //       url: "/registerhospital/",
   //       }).then ( function( json, textStatus, jqXHR ) {
   //          json["data"] = json;
   //          callback(json);
   //       });
   //    },
   //    columns: [
   //       { data: "HOSPITAL" },
   //       { data: "AMBITO" },
   //       { data: "IDENTIFICADOR" },
   //       { data: "IDURGENCIAS" },
   //       { data: "CIP" },
   //       { data: "FECNAC" },
   //       { data: "SEXO" },
   //       { data: "RESIDECP"},
   //       { data: "RESIDEMUNI"},
   //       { data: "PAISNAC"},
   //       { data: "FECING"},
   //       { data: "FECINGHOSP"},
   //       { data: "UCI"},
   //       { data: "DIASUCI"},
   //       { data: "FECALT"},
   //       { data: "TIPALT"},
   //       { data: "D1"},

   //    ]
   // });

   /**
    * Load all diagnostic from DataBase
    */

   $("#diagnostic-code").dataTable({
      paging: true,
      deferRender: true,
      ajax: function (data, callback, settings) {
         console.log(data)
         // Call service registerCodedD1 -> tengo que cambiar el nombre
         $.ajax({
            url: "/registercoded1/",
         }).then(function (json, textStatus, jqXHR) {
            json["data"] = json;
            callback(json);
            console.log(json)
         });
      },
      columns: [
         { data: "code" },
         { data: "description" },
         {
            //Last Column add function button Analisys
            // Create cell dynamic with link for analysis code. 
            "data": "code",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
               $(nTd).html("<a class='btn btn-primary' href='/analysis_code_diagnostic/"+oData.code+"'> Analizar </a>");
            }            
         }
      ],

   });

   $('#diagnostic-code tbody').on('click', 'tr', async function () {


      if ($(this).hasClass('selected')) {
         $(this).removeClass('selected');
      }
      else {
         /**
          * Code where load sweetalert2
          */
         $(this).addClass('selected');
         const ipAPI = 'registerfieldcolumn/'

         const inputValue = await fetch(ipAPI)
            .then(response => response.json())
         console.log(inputValue)
         var html_check = ""


         var last_category = "";
         var first_time = true;
         for (c = 0; c < inputValue.length; c++) {
            var category = inputValue[c].category_field_column;

            if (category != last_category) {
               if (first_time != true) { html_check += '</div></div>' } //Close card-primary and card-body 
               first_time = false;
               html_check += '<div class="card card-primary"><div class="card-header"><h3 class="card-title">' + category + '</h3>' +
                  '<div class="card-tools">' +
                  '<!-- This will cause the card to collapse when clicked -->' +
                  '<button type="button" class="btn btn-tool" data-card-widget="collapse"><i class="fas fa-minus"></i></button>' +
                  '</div>' +
                  '<!-- /.card-tools -->' +
                  '</div>' +
                  '<!-- /.card-header -->' +
                  '<div class="card-body">'
               // html_check += "<h3>"+inputValue[c].category_field_column + "</h3>"
               last_category = inputValue[c].category_field_column
            }



            html_check += "<div class='col-6' style='text-align:left; display:inline-block'><input id=" +
               inputValue[c].name_field_column + " class='cursor-pointer' name=" + inputValue[c].name_field_column + " type='checkbox'><span class='cursor-pointer' title='" + inputValue[c].description_field_column +
               "'> " + inputValue[c].name_field_column + "</span></input></div>"

         }
         /**
          * Variable where save name code.
          */
         var code = $(this).children().html()
         /**
          * Configure sweetalert2
          */
         const { value: formValues } = Swal.fire({
            title: 'Seleccione los campos que desee',
            html: html_check,
            focusConfirm: false,
            preConfirm: () => {
               var selected = [];
               $('div input:checked').each(function () {
                  selected.push(($(this).attr('name')));
               })
               return [selected]
            }
         }).then(function (result) {
            if (result) {
               /**
                * Destroy datatable 
                */
               $("#first-data").DataTable().clear().destroy();
               $('#first-data tbody').empty();
               $('#first-data thead').empty();
               $('#first-data tfoot').empty();

               /**
                * Create new datatable when fields selections in sweetalert
                */
               array = []
               for (c = 0; c < result.value[0].length; c++) {
                  dictionary = { title: result.value[0][c] }
                  /**
                   * { 'title: field_column } 
                   */
                  array.push(dictionary)
               }

               $.ajax({
                  type: 'GET',
                  url: "registerdynamicdatatable/",
                  data: { "columns": array, "code": code },
                  success: function (response) {
                     console.log(response)
                     array_data
                     data_set = array_row
                     /**
                      * Fill new Datatable with new data.
                      *  
                      * */
                     $('#first-data').DataTable({
                        paging: true,
                        deferRender: true,
                        columns: array,
                        data: data_set,
                     })
                  }
               });
               /**
                * Dynamic Small Box
                */
               $.ajax({
                  type: 'GET',
                  url: "registerdynamicsmallbox/",
                  data: { "code": code },
                  success: function (response) {

                     $("#diagnostic_register").text(response[0]['diagnostic_register'])
                     $("#diagnostic_register_died").text(response[0]['diagnostic_died'])
                     $("#diagnostic_uci").text(response[0]['diagnostic_register_uci'])
                     $("#diagnostic_register_alta").text(response[0]['diagnostic_register_altas'])
                     $(".name_code").text(response[0]['name_d1'])
                  }

               });

               $.ajax({
                  type: 'GET',
                  url: "registerdynamicuci/",
                  data: { "code": code },
                  success: function (response) {

                     /**
                      * Create new Dynamic areaChart 
                      */
                     var labels_month = []
                     var uci_month = []
                     var name_d1 = response[0]['name_d1']

                     $(".title-uci").text("Ingresos en UCI por " + name_d1)

                     for (c = 0; c < response.length; c++) {
                        labels_month.push(response[c]['date'])
                        uci_month.push(response[c]['uci'])
                     }
                     $('#areaChart').remove();
                     $("#chartArea").append('<canvas id="areaChart" style="min-height: 250px; height: 250px; max-height: 250px; max-width: 100%;"></canvas>');

                     /**
                     * Dictionary config every charts. 
                     */datadataset['pointStrokeColor'] = '#fff',
                        config_dataset['pointHighlightFill'] = 'rgba(60,141,188,1)',
                        config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
                        config_dataset['data'] = uci_month

                     config_data['datasets'].push(config_dataset);

                     config_char_options['maintainAspectRatio'] = false,
                        config_char_options['responsive'] = true,
                        config_char_options['legend'] = { display: false },
                        config_char_options['scales'] = {
                           xAxes: [{ gridLines: { display: false, } }],
                           yAxes: [{ gridLines: { display: false, } }]
                        }
                     createAreaChartJs(config_data, config_char_options, '#areaChart', 'areaChart');
                  }
               });

               $.ajax({
                  type: 'GET',
                  url: "registerdynamictimeseries/",
                  data: { "code": code },
                  success: function (response) {
                     /**
                      * Create new Dynamic LineChart 
                      */
                     var labels_month = []
                     var register_month = []
                     var name_d1 = response[0]['name_d1']

                     $(".title-line_register").text("Número de Ingresos  por " + name_d1)

                     dataata['datasets'] = []

                     config_dataset['label'] = 'Número de Ingresos',
                        config_dataset['backgroundColor'] = 'rgba(60,141,188,0.9)',
                        config_dataset['borderColor'] = 'rgba(60,141,188,0.8)',
                        config_dataset['pointRadius'] = false,
                        config_dataset['pointColor'] = '#3b8bba',
                        config_dataset['pointStrokeColor'] = '#fff',
                        config_dataset['pointHighlightFill'] = 'rgba(60,141,188,1)',
                        config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
                        config_dataset['data'] = register_month
                     config_data['datasets'].push(config_dataset);

                     config_char_options['maintainAspectRatio'] = false,
                        config_char_options['responsive'] = true,
                        config_char_options['legend'] = { display: false },
                        config_char_options['scales'] = {
                           xAxes: [{ gridLines: { display: false, } }],
                           yAxes: [{ gridLines: { display: false, } }]
                        }
                     createAreaChartJs(config_data, config_char_options, '#lineChart', 'linearChart');
                  }
               });

               //-------------
               //- BAR CHART -
               //-------------

               $.ajax({
                  method: "GET",
                  url: "registerdynamicbartimeseries/",
                  data: { "code": code },
                  success: function (result) {

                     /**
                     * Create new Dynamic BarChart
                     */

                     var labels_month = []
                     var baritems_month = []
                     var name_d1 = result[0]['name_d1']
                     $(".title-bar-register").text("Evolución de Ingresos  por " + name_d1)

                     for (c = 0; c < result.length; c++) {
                        labels_month.push(result[c]['date'])
                        baritems_month.push(result[c]['baritems'])
                     }

                     $('#barChart').remove();
                     $('#chartBar').append('<canvas id="barChart" style="min-height: 250px; height: 250px; max-height: 250px; max-width: 100%;"></canvas>');

                     /**
                     * Dictionary config every charts. 
                     */
                     config_data = {}
                     config_dataset = {}
                     config_char_options = {}

                     config_data['labels'] = labels_month
                     config_data['datasets'] = []

                     config_dataset['label'] = 'Evolución diagnostico',
                        config_dataset['backgroundColor'] = 'rgba(60,141,188,0.9)',
                        config_dataset['borderColor'] = 'rgba(60,141,188,0.8)',
                        config_dataset['pointRadius'] = false,
                        config_dataset['pointColor'] = '#3b8bba',
                        config_dataset['pointStrokeColor'] = 'rgba(60,141,188,1)',
                        config_dataset['pointHighlightFill'] = '#fff',
                        config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
                        config_dataset['data'] = baritems_month
                     config_data['datasets'].push(config_dataset);

                     config_char_options['maintainAspectRatio'] = false,
                        config_char_options['responsive'] = true,
                        config_char_options['legend'] = { display: false },
                        config_char_options['scales'] = {
                           xAxes: [{ gridLines: { display: true, } }],
                           yAxes: [{ gridLines: { display: true, } }]
                        }
                     createAreaChartJs(config_data, config_char_options, '#barChart', 'bar');
                  }
               });

            }
         })
      }
   });
});

