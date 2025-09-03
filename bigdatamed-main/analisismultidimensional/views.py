from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import Template, Context
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import ModeloEjemplo
from dashboard.models import Experiment
import json
import ast
import requests
from django.views.decorators.csrf import csrf_exempt
import base64


@login_required
def home(request):
    return render(request, "home_am.html", locals())
   
# Función que bbtiene las columnas de la experimentación que se seleccione
@login_required
def obtenerColumnas(request):
    if request.method == 'GET':
        nombre_experimentacion = request.GET.get('nombre_experimentacion')
    
         # Obtenemos la experimentación seleccionada
        experimentacion = get_object_or_404(Experiment, name=nombre_experimentacion)

    
        # Obtenemos las columnas en cadena de texto
        filter_apply_str = experimentacion.filter_apply
        print("Las columnas son: ", filter_apply_str)

        filter_apply_dict = ast.literal_eval(filter_apply_str)
        columnas = filter_apply_dict.get('selected_variables', [])
      
        # Devolvemos las columnas en formato JSON
        return JsonResponse({'columnas':columnas})
    
    else:  
        return JsonResponse({'error' : 'Método no permitido'}, status=405)

# Función que obtiene las filas de una base de datos
@login_required
def obtenerFilas(request):
    if request.method == 'GET':
        nombre_bd = request.GET.get('nombre_bd')
        response = requests.get(f"http://localhost:5000/bigdatamed/{nombre_bd}/data")
        data = response.json()

        request.session['filas'] = data

        return JsonResponse({'filas':data})

# Obtiene las experimentaciones asociadas a una base de datos
@login_required
def obtenerExperimentaciones(request):
    if request.method == 'GET':
        nombre_bd = request.GET.get('nombre_bd') 
        request.session['nombredb'] = nombre_bd

        # Obtenemos las experimentaciones
        experimentaciones = Experiment.objects.filter(name_bbdd=nombre_bd)
        experimentaciones_info = ""

        experimentaciones_info = [str(experimentacion.date_create) + " / " + experimentacion.name for experimentacion in experimentaciones]

        return JsonResponse({'experimentaciones':experimentaciones_info})
    
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

# Función que obtitne los metadatos de una base de datos
@login_required
def obtenerMetadatos(request):
    if request.method == 'GET':
       
        nombre_bd = request.GET.get('nombre_bd')
      
        response = requests.get(f"http://localhost:5000/bigdatamed/{nombre_bd}/meta")
        data = response.json()

        return JsonResponse({'metadatos':data})


# Función que bbtiene los cubos de la petición a la API
@login_required
def obtenerCubos(request):
     if request.method == 'GET':
        user = request.user
       
        #Llamada a la API
        response = requests.get(f"http://servicios_olap:8001/analisismultidimensional/getCubes/{user}")
        data = response.json()
       
        #Devolvemos array de json
        return JsonResponse({'cubos':data})

# Función que llama a la API para crear un cubo
@login_required
def crearCubo(request):
    if request.method == 'GET':
        #Cogemos todas las experimentaciones del usuario
        all_experiments = Experiment.objects.filter(user=request.user.pk).order_by('-date_create')
        user = request.user
        
        return render(request, "crear_cubo.html", locals())
    
    else:
        cubo_data = request.POST.get('cubo')
        cubo = json.loads(cubo_data)

        propiedades = {
            "propiedades": cubo
        }

        #Recuperamos valor de medida
        medida = propiedades['propiedades']['medida']

        #Recuperamos los niveles
        niveles = []

        def obtenerNiveles(dimensiones):
            for dimension in dimensiones.values():
                jerarquias = dimension.get("jerarquias", {})
                for jerarquia in jerarquias.values():
                    niveles_jerarquia = jerarquia.get("niveles", [])
                    niveles.extend(niveles_jerarquia)

       
        obtenerNiveles(cubo['dimensiones'])
        niveles.append(medida)

        #Ahora los datos obtenidos de mongo los filtramos según los niveles que hemos seleccionado.
        #Seleccionamos sólo los documentos que tengan todos los niveles que hemos seleccionado
        filas = request.session['filas']
      
        filas_filtradas = []

        for obj in filas:
            if all(nivel in obj for nivel in niveles):
                obj_filtrado = {nivel: obj[nivel] for nivel in niveles}
                filas_filtradas.append(obj_filtrado)

        #Guardamos las filas
        filas = {
            "filas": filas_filtradas
        }

        propiedadesjson = json.dumps(propiedades)
        filasjson = json.dumps(filas)
        
        #Creamos un json con la estructura, y luego las filas
        data = {
            "estructura": cubo,
            "datos": filas
        }

        datajson = json.dumps(data)
        
        #Petición POST a la API para crear el cubo
        responseModel = requests.post("http://servicios_olap:8001/analisismultidimensional/createCubeModel/", json=propiedades)
        response_model_data = responseModel.json()
        
        if (response_model_data['detail'] == "Ya existe un cubo con ese nombre"):
            print("Ya existe un cubo con ese nombre")
            return JsonResponse({'error' : 'Ya existe un cubo con ese nombre'})
        else:
            responseDw = requests.post("http://servicios_olap:8001/analisismultidimensional/createCubeDW/", data=datajson)
            print("Status code:", responseDw.status_code)
            print("Raw text:", responseDw.text)
            response_dw_data = responseDw.json()
            print("DATOS DE RESPUESTA DE LA API DW: ", response_dw_data);
            return JsonResponse({'success' : 'Cubo enviado a la API'})
        
        
# Función que renderiza la página de Ver Cubos
@login_required
def verCubos(request):
    if request.method == 'GET':

    return render(request, "explorar_cubos.html", locals())

# Función que renderiza la página de información del cubo
@login_required
def cuboInfo(request):
    if request.method == 'GET':
        cuboData = base64.b64decode(request.GET.get('cubo'))
        
        return render(request, "cubo_info.html", locals())

        
