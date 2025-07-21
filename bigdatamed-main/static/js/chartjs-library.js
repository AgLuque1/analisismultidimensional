function createAreaChartJs(config_data, config_char_options, identification,type_chart ){
        
    var type = 'line';
    var areaChartCanvas = $(identification).get(0).getContext('2d')
    var areaChartData = {
      config_data
    }
    var areaChartOptions = {
      config_char_options
    }

    /**
     * Different options, depends type charts.
     */
    if (type_chart =="linearChart"){
      areaChartOptions = $.extend(true, {}, areaChartOptions)
      areaChartData = $.extend(true, {}, areaChartData)
      areaChartData.config_data.datasets[0].fill = true;
      areaChartOptions.config_char_options.datasetFill = true

    }

    if (type_chart == 'doughnut'){
      type=type_chart
    }

    if ( type_chart== "bar"){
      areaChartData = $.extend(true, {}, areaChartData);
      type = type_chart;
    }

    // This will get the first returned node in the jQuery collection.
    new Chart(areaChartCanvas, {
      type: type,
      data: areaChartData['config_data'],
      options: areaChartOptions['config_char_options']
    })
}


