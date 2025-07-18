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
   
# Obtiene las columnas de la experimentación que se seleccione
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
      
        '''
        # Reformateamos la cadena de texto para poder convertirlo en diccionario
        filter_apply_str_reformated = filter_apply_str.replace("'", "\"")

        # Transformarmos las columnas en diccionario, porque vienen en cadena de texto
        filter_apply_dict = json.loads(filter_apply_str_reformated)

        # Obtenemos las columnas
        columnas = filter_apply_dict.get('selected_variables', [])
        '''
        
        # Devolvemos las columnas en formato JSON
        return JsonResponse({'columnas':columnas})
    
    else:  
        return JsonResponse({'error' : 'Método no permitido'}, status=405)
    
@login_required
def obtenerFilas(request):
    if request.method == 'GET':
        print("Dentro de la peticion de obtener filas")
        nombre_bd = request.GET.get('nombre_bd')

        print("Haciendo request a la api de bigdatamed de las filas")

        response = requests.get(f"http://localhost:5000/bigdatamed/{nombre_bd}/data")

        data = response.json()

        request.session['filas'] = data

        print("PETICION DE FILAS FINALIZADA ")

        return JsonResponse({'filas':data})

# Obtiene las experimentaciones asociadas a una bd
@login_required
def obtenerExperimentaciones(request):
    if request.method == 'GET':
        print("Dentro de la peticion experimentaciones")
        nombre_bd = request.GET.get('nombre_bd') 

        request.session['nombredb'] = nombre_bd

        # Obtenemos las experimentaciones
        experimentaciones = Experiment.objects.filter(name_bbdd=nombre_bd)
        print("Las experimentaciones asociadas son: ", experimentaciones)

        experimentaciones_info = ""

        experimentaciones_info = [str(experimentacion.date_create) + " / " + experimentacion.name for experimentacion in experimentaciones]
        print("Las experimentaciones formateadas son: ", experimentaciones_info)

        return JsonResponse({'experimentaciones':experimentaciones_info})
    
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@login_required
def obtenerMetadatos(request):
    if request.method == 'GET':
       
        nombre_bd = request.GET.get('nombre_bd')
      
        response = requests.get(f"http://localhost:5000/bigdatamed/{nombre_bd}/meta")

        data = response.json()

        #print("Datos de meta:", data)


        return JsonResponse({'metadatos':data})


# Obtiene los cubos de la petición a la API
@login_required
def obtenerCubos(request):
     if request.method == 'GET':
        print("Dentro del get de obtenerCubos")
        user = request.user
        print("El user es")
        print(user)
        #Llamada a la API
        
        #response = requests.get(f"http://localhost:8001/analisismultidimensional/getCubes/{user}")
        response = requests.get(f"http://servicios_olap:8001/analisismultidimensional/getCubes/{user}")
        data = response.json()
        print("DATOS DE RESPUESTA DE LA API: ", data)
        #return render(request, "explorar_cubos.html", {"data": data})

        #Devolvemos array de jsons
        print("Devolviendo resultados")
        return JsonResponse({'cubos':data})


@login_required
def crearCubo(request):
    if request.method == 'GET':
        print("Dentro de get de crear cubo")
        #Cogemos todas las experimentaciones del usuario
        all_experiments = Experiment.objects.filter(user=request.user.pk).order_by('-date_create')
        user = request.user
        
        return render(request, "crear_cubo.html", locals())
    
    else:
        print("Dentro solicitud POST")
        cubo_data = request.POST.get('cubo')

        print("Haciendo peticion desde POST")

        
        print("Cubo recibido en la vista. Mostrando info cubo_data")
        print(cubo_data);

        cubo = json.loads(cubo_data)

        propiedades = {
            "propiedades": cubo
        }

        #Recuperamos valor de medida
        medida = propiedades['propiedades']['medida']
        print("Medida: " , medida)

        #Recuperamos los niveles
        niveles = []

        def obtenerNiveles(dimensiones):
            for dimension in dimensiones.values():
                jerarquias = dimension.get("jerarquias", {})
                for jerarquia in jerarquias.values():
                    niveles_jerarquia = jerarquia.get("niveles", [])
                    niveles.extend(niveles_jerarquia)

       
        obtenerNiveles(cubo['dimensiones'])
        #niveles = list(obtenerNiveles(cubo['dimensiones']))
        niveles.append(medida)

        print("DATOS FILTRADOS, IMPRIMIENDO: ", niveles)

        #Ahora los datos obtenidos de mongo los filtramos según los niveles que hemos seleccionado.
        #Seleccionamos sólo los documentos que tengan todos los niveles que hemos seleccionado
        filas = request.session['filas']
        #print("Datos de mongo, todas las filas: ", filas)

        print("\n")

        filas_filtradas = []

        for obj in filas:
            if all(nivel in obj for nivel in niveles):
                obj_filtrado = {nivel: obj[nivel] for nivel in niveles}
                filas_filtradas.append(obj_filtrado)

        print("Filas FILTRADAS: ", filas_filtradas)

        #Peticion para guardar las filtradas en json en una base de datos
        #filas_json = json.dumps(filas_filtradas)
       

        #print("Filas filtradas JSON: ", filas_json)
        
        filas = {
            "filas": filas_filtradas
        }

    
        #print("Data con las propiedades")
        #print(propiedades)

        print("Data con las propiedades")
        propiedadesjson = json.dumps(propiedades)
        print(propiedadesjson)


        print("Data con las filas")
        filasjson = json.dumps(filas)
        print(filasjson)

        #Crear un json con la estructura, y luego las filas
        data = {
            "estructura": cubo,
            "datos": filas
        }

        datajson = json.dumps(data)
        print ("Datos conjuntos json: ", datajson)
        
        #print ("Datos conjuntos: ", data)

        print("Haciendo la peticion a la API")

        #Petición POST a la API para crear el cubo
        #responseModel = requests.post("http://localhost:8001/analisismultidimensional/createCubeModel/", json=propiedades)
        responseModel = requests.post("http://servicios_olap:8001/analisismultidimensional/createCubeModel/", json=propiedades)
        response_model_data = responseModel.json()
        
      

        print("DATOS DE RESPUESTA DE LA API MODEL: ", response_model_data);
        #print("DATOS DE RESPUESTA DE LA API DW: ", response_dw_data);
        
        if (response_model_data['detail'] == "Ya existe un cubo con ese nombre"):
            print("Ya existe un cubo con ese nombre")
            return JsonResponse({'error' : 'Ya existe un cubo con ese nombre'})
        else:
            #Petición POST a la API para crear el cubo dw
            #responseDw = requests.post("http://localhost:8001/analisismultidimensional/createCubeDW/", data=datajson)
            responseDw = requests.post("http://servicios_olap:8001/analisismultidimensional/createCubeDW/", data=datajson)
            print("Status code:", responseDw.status_code)
            print("Raw text:", responseDw.text)
            response_dw_data = responseDw.json()
            print("DATOS DE RESPUESTA DE LA API DW: ", response_dw_data);
            return JsonResponse({'success' : 'Cubo enviado a la API'})
        
        
    
@login_required
def verCubos(request):
    if request.method == 'GET':
        print("Dentro del get de ver")
      

    return render(request, "explorar_cubos.html", locals())

@login_required
def cuboInfo(request):
    if request.method == 'GET':
        print("/n")
        print(request.GET.get('cubo'))
        cuboData = base64.b64decode(request.GET.get('cubo'))
        print("Recibiendo información del cubo en Info")
        print(cuboData)

        return render(request, "cubo_info.html", locals())

"""
    else:
        dataCubo = request.POST.get('cubo');
        print("Cubo recibido de la tabla. Mostrandolo")
        print(dataCubo)
        #return redirect('/analisismultidimensional/cubo-info')
        
"""  
        