from django.urls import path,include
from machinelearning import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'machinelearning'
urlpatterns = [
    path(r'', views.home, name='home'),
    path(r'result-experiment', views.result_execute_experiment, name='result_experiment'),
    # path(r'ml-upload-csv', views.MLUploadCsvView, name='ML_upload_csv'),
    # path(r'ml-display-filter-data/<str:order_variable>', views.MLDisplayFilterDataView, name='ML_display_filter_data'),
    # path(r'ml-reset-filter/<str:view_calling>', views.MLResetFilter, name='ML_reset_filter'),
    # path(r'ml-erase-table', views.MLEraseTable, name='ML_erase_table'),
    # path(r'ml-detail/<str:id_detail>/', views.MLDetailView, name='ML_detail'),
    # path(r'ml-eda-index', views.MLEDAIndexView, name='ML_eda_index'),
    # path(r'ml-eda/<str:eda_variable>/<str:eda_variable2>', views.MLEDAView, name='ML_eda'),
    # path(r'ml-algorithm-selection/<str:problem_string>', views.MLAlgorithmSelectionView, name='ML_algorithm_selection'),
    # path(r'ml-select-variable/<str:operation>', views.MLSelectVariableView, name='ML_select_variable'),
    # path(r'ml-select-target', views.MLSelectTargetView, name='ML_select_target'),
    # path(r'ml-cluster-set-up', views.MLClusterSetUpView, name='ML_cluster_set_up'),
    # path(r'ml-algorithm-selection/<str:problem_string>', views.MLAlgorithmSelectionView, name='ML_algorithm_selection'),
    # path(r'ml-algorithm-set-up', views.MLAlgorithmSetUpView, name='ML_algorithm_set_up'),
    # path(r'ml-previous-results', views.MLPreviousResultsView, name='ML_previous_results'),
    # path(r'ml-result-analysis/<str:algorithm_string>/<str:id_instance>', views.MLResultAnalysisView, name='ML_result_analysis'),
    # path(r'ml-dataset-config', views.MLDatasetConfigView, name='ML_dataset_config'),
    # path(r'ml-show-cards/<int:id_parent>', views.MLShowCardsView, name='ML_show_cards'),
    # path(r'ml-build-complex-filter/<str:operation>', views.MLBuildComplexFilter, name='ML_build_complex_filter'),
    # path(r'ml-activate-previous-config/<str:id_previous_config>', views.MLActivatePreviousConfig, name='ML_activate_previous_config'),
    # path(r'ml-create-subset', views.MLCreateSubsetView, name='ML_create_subset'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
