
from django.urls import path,include
from dashboard import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard'
urlpatterns = [
   path(r'', views.home, name='home'),
   path(r'create-experimentation', views.createExperimentationView, name='create_experimentation'),  
   path(r'config-dataset', views.configDatasetView, name='config_dataset'),  
   path(r'load_experiment/<str:operation>', views.load_experiment, name='load_experiment'),  
   path(r'filter-dataset', views.filter_dataset, name='filter_dataset'), 
   path(r'manage-filter', views.manage_filter, name='manage_filter'), 
   path(r'problem-selection', views.problemSelectionView, name='problem_selection'),
   path(r'algorithm-selection-setup/<str:problem_string>', views.algorithmSelectionSetupView, name='algorithm_selection_setup'), 
   path(r'ajax/remove-exp-table/<id_exp>', views.remove_exp_table, name='remove_exp_table'),  
   path(r'ajax/plot_variable', views.plot_variable, name='plot_variable'),
   path(r'ajax/get_filter_variable_dictionary', views.get_filter_variable_dictionary, name='get_filter_variable_dictionary'),
   path(r'ajax/get_info_parameters_algorithm', views.get_info_parameters_algorithm, name='get_info_parameters_algorithm'),
   path(r'ajax/run_elbow_method', views.run_elbow_method, name='run_elbow_method'),  
   path(r'ajax/run_algorithm', views.run_algorithm, name='run_algorithm'),
   path(r'ajax/get_distributed_parameters', views.get_distributed_parameters, name='get_distributed_parameters'),
   path(r'profile', views.profile_user, name='profile_user'),  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
