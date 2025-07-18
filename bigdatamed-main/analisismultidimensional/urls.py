from django.urls import path,include
from analisismultidimensional import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'analisismultidimensional'
urlpatterns = [
   path(r'', views.home, name='home'),
   path(r'crear-cubo', views.crearCubo, name='crear_cubo'),
   path(r'cubos', views.verCubos, name='cubos'),
   path(r'obtener-columnas', views.obtenerColumnas, name='obtener_columnas'),
   path(r'obtener-experimentaciones', views.obtenerExperimentaciones, name='obtener_experimentaciones'),
   path(r'obtener-meta', views.obtenerMetadatos, name='obtener_metadatos'),
   path(r'obtener-filas', views.obtenerFilas, name='obtener_filas'),
   path(r'obtener-cubos', views.obtenerCubos, name='obtener-cubos'),
   path(r'cubo-info', views.cuboInfo, name='cubo_info')
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
