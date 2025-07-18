# DashBoard BigDataMed
En esta parte del repositorio se expondrá como está estructurada la aplicación. A continuación se explicarán en que consisten cada uno de los archivos html que conforman la estructura de nuestra aplicación. 

## Vista Creación de Experimentación

Esta vista es la encargada de dar  al usuario la posibilidad de crear una nueva experimentación o si por el contrario necesita seguir trabajando en alguna experimentación ya realizada. 

Los siguientes ficheros son los encargados de ejecutar esta vista:

- models.py [ class Experiment(models.Model) ]
- url.py  [ path(r'create-experimentation', views.createExperimentationView, name='create_experimentation') ]
- view.py [ def createExperimentationView(request)  ]
- create-experimentation.html

A continuación, pasamos a comentar la vista. 

### create-experimentación.html
Este fichero es el fichero que se ejecuta en cuanto el usuario se logea de forma correcta en nuestro sistema. En este fichero se puede diferenciar dos partes:

- Una primera parte donde se puede crear una nueva experimentación.
- Una segunda parte donde se puede cargar una experimentación anteriormente realizada.

###  Nueva experiementación
En esta parte el sistema cargará las bases de datos que están disponibles en nuestra apiRest. En este caso los servicios que suministrarán al sistema  la carga de las bases de  datos sería:

- settings.URL_CONFIG_API_REST + 'getAdminDBVerbose'

Los demás campos del formulario son simplemente una texto donde se guardará el nombre identificativo de nuestra experimentación y dos tipos de datos fecha init y fecha fin por si necesitamos partir nuestra base de datos.

Aquí podemos ver un ejemplo de llamada de un servicio a nuestra apiRest.

```
    all_bbdd = requests.get(settings.URL_CONFIG_API_REST + getAdminDBVerbose)       
        
    all_bbdd = json.loads(all_bbdd.text)
    listof_dict_aux = []
    for elem in all_bbdd:
        dict_aux = dict()
        dict_aux[elem["dataset"]] = elem["verbose"]
        listof_dict_aux.append(dict_aux)
    
    all_bbdd = listof_dict_aux
    all_bbdd_dictionary = {k: v for element in all_bbdd for k, v in element.items()}
```


### Cargar Experimentación. 
Esta parte del sistema se encargará de cargar los datos ya creados en nuestra aplicación. Estas experimentaciones están almacenadas en forma de texto  en nuestro sistema. Como se dijo en la primera parte estos datos están almacenados en forma de texto en nuestro Dashboard, ya que, solo está almacenada la parte de la configuración de la experimentación no necesita los propios datos de la base de datos. 

Para obtener las diferentes experimentaciones tan solo se necesita llamar al modelo donde se almacenan las experimentaciones y pintarlas en nuestro html. 

## Vista selección de variables



## Vista filtrado de datos


## Vista selección del tipo de algoritmos a ejecutar







