

$(function () {
    /* ChartJS
     * -------
     * Here we will create a few charts using ChartJS
     */

    //--------------
    //- AREA CHART -
    //--------------
    // Get context with jQuery - using jQuery's .get() method.   
        
    $.ajax({
      method: "GET",
      url: "registeruci/",
      success: function(result){
        console.log(result);
        
        var labels_month =[]
        var uci_month =[]
        var name_d1 = result[0]['name_d1']

        // $(".title-uci").text("Ingresos en UCI por " + name_d1)

         /**
         * Constructor Array labels Months and uci registers every months
         */
        for (c=0; c < result.length; c++){
          labels_month.push(result[c]['date'])
          uci_month.push(result[c]['uci'])}

        /**
         * Dictionary config every charts. 
         */
        config_data             = {}
        config_dataset          = {}
        config_char_options     = {}
        
        config_data['labels'] = labels_month
        config_data['datasets']= []

        config_dataset['label']                = 'Ingresos UCI',
        config_dataset['backgroundColor']      = 'rgba(60,141,188,0.9)',
        config_dataset['borderColor']          = 'rgba(60,141,188,0.8)',
        config_dataset['pointRadius']          =  false,
        config_dataset['pointColor']           = '#3b8bba',
        config_dataset['pointStrokeColor']     = '#fff',
        config_dataset['pointHighlightFill']   = 'rgba(60,141,188,1)',
        config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
        config_dataset['data']                 =  uci_month
        
        config_data['datasets'].push(config_dataset);
        
        config_char_options['maintainAspectRatio'] = false,
        config_char_options['responsive']          = true,
        config_char_options['legend'] = { display: false },
        config_char_options['scales'] ={ xAxes: [{ gridLines : {display : false,} }],
                                         yAxes: [{ gridLines : {display : false,} }]
                                      }
        createAreaChartJs(config_data, config_char_options, '#areaChart','areaChart');
      } //END SUCCESS
    }); //END $AJAX


    //-------------
    //- LINE CHART -
    //--------------

    $.ajax({
      method: "GET",
      url: "registertime/",
      success: function(result){
        console.log(result);
        
        var labels_month =[]
        var D1_month =[]
        // var name_d1 = result[0]['name_d1']

        // $(".title-line_register").text("Número de ingrersos  por " + name_d1)

         /**
         * Constructor Arraya Labels Month and bartitems every months
         */
        
        for (c=0; c < result.length; c++){
          labels_month.push(result[c]['date'])
          D1_month.push(result[c]['diagnostic_month'])         
        }
        /**
         * Dictionary config every charts. 
         */
         config_data             = {}
         config_dataset          = {}
         config_char_options     = {}
         
         config_data['labels'] = labels_month
         config_data['datasets']= []
 
         config_dataset['label']                = 'Ingresos UCI',
         config_dataset['backgroundColor']      = 'rgba(60,141,188,0.9)',
         config_dataset['borderColor']          = 'rgba(60,141,188,0.8)',
         config_dataset['pointRadius']          =  false,
         config_dataset['pointColor']           = '#3b8bba',
         config_dataset['pointStrokeColor']     = '#fff',
         config_dataset['pointHighlightFill']   = 'rgba(60,141,188,1)',
         config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
         config_dataset['data']                 =  D1_month
         config_data['datasets'].push(config_dataset);

         config_char_options['maintainAspectRatio'] = false,
         config_char_options['responsive']          = true,
         config_char_options['legend'] = { display: false },
         config_char_options['scales'] ={ xAxes: [{ gridLines : {display : false,} }],
                                          yAxes: [{ gridLines : {display : false,} }]
                                        }
         createAreaChartJs(config_data, config_char_options, '#lineChart','linearChart');
      } //END SUCCESS
    }); //END $AJAX
    
    
    //-------------
    //- DONUT CHART -
    //-------------
    $.ajax({
      method: "GET",
      url: "registerdiagnostic/",
      success: function(result){
                
        var list_diagnostics = []
        var list_data = []    
        
         /**
         * Constructor Arraya Labels Month and bartitems every months
         */
        
        for (c=0; c < result.length; c++){
           list_diagnostics.push(result[c]['diagnostic'])
           list_data.push(result[c]['num_diagnostic'])
        }
        /**
         * Dictionary config every charts. 
         */
         config_data             = {}
         config_dataset          = {}
         config_char_options     = {}
         
         list_colors = ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de','#d2d6de','#d2d6de','#d2d6de','#d2d6de'];
         config_data['labels'] = list_diagnostics;
         config_data['datasets']= [];
         
         config_dataset['data'] = list_data;
         config_dataset['backgroundColor'] = list_colors;
         config_data['datasets'].push(config_dataset);
         
         config_char_options['maintainAspectRatio'] = false,
         config_char_options['responsive']          = true,
         config_char_options['legend'] = { display: true },
         config_char_options['scales'] ={ xAxes: [{ gridLines : {display : false,} }],
                                          yAxes: [{ gridLines : {display : false,} }]
                                        }
        createAreaChartJs(config_data, config_char_options, '#donutChart','doughnut');
      } //END SUCCESS
    }); //END $AJAX

    
    //-------------
    //- BAR CHART -
    //-------------

    $.ajax({
      method: "GET",
      url: "registerbar/",
      success: function(result){
      
        console.log(result);
        
        var labels_month =[]
        var baritems_month =[]
        

       

        /**
         * Constructor Arraya Labels Month and bartitems every months
         */
        for (c=0; c < result.length; c++){
          labels_month.push(result[c]['date'])
          baritems_month.push(result[c]['baritems'])
        }

        /**
         * Dictionary config every charts. 
         */
        config_data             = {}
        config_dataset          = {}
        config_char_options     = {}
        
        config_data['labels'] = labels_month
        config_data['datasets']= []

        config_dataset['label']                = 'Evolución diagnostico',
        config_dataset['backgroundColor']      = 'rgba(60,141,188,0.9)',
        config_dataset['borderColor']          = 'rgba(60,141,188,0.8)',
        config_dataset['pointRadius']          =  false,
        config_dataset['pointColor']           = '#3b8bba',
        config_dataset['pointStrokeColor']     = 'rgba(60,141,188,1)',
        config_dataset['pointHighlightFill']   = '#fff',
        config_dataset['pointHighlightStroke'] = 'rgba(60,141,188,1)',
        config_dataset['data']                 =  baritems_month
        config_data['datasets'].push(config_dataset);

        config_char_options['maintainAspectRatio'] = false,
        config_char_options['responsive']          = true,
        config_char_options['legend'] = { display: false },
        config_char_options['scales'] ={ xAxes: [{ gridLines : {display : true,} }],
                                         yAxes: [{ gridLines : {display : true,} }]
                                       }
        createAreaChartJs(config_data, config_char_options, '#barChart','bar');
       
      } //END SUCCESS
    }); //END $AJAX
      
}) 