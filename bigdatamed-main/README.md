# BIGDATAMED
Este repositorio es el encargado de la interfaz de usuario BIGDATAMED. Este tipode de interfeaces se pueden utilizar para cualquier dominio que se quiera usar. 

La idea principal de este tipo de interfaces es la oportunidad de reutilizar el código mediante la utilización de diferentes apis que nos den la posiblidad de mostrar lo que necesita en cada instante, provocando que se a independiente del  dominio que aborda.

Esta interfaz está desarrollada con el framework Djano  por lo que resulta esencial tener un conocimiento básico de este tipo de framework https://docs.djangoproject.com/en/4.1/.

Aquí podemos ver un ejemplo de llamada de un servicio a nuestra apiRest.

<code>

    all_bbdd = requests.get(settings.URL_CONFIG_API_REST + getAdminDBVerbose)       
        
    all_bbdd = json.loads(all_bbdd.text)
    listof_dict_aux = []
    for elem in all_bbdd:
        dict_aux = dict()
        dict_aux[elem["dataset"]] = elem["verbose"]
        listof_dict_aux.append(dict_aux)
    
    all_bbdd = listof_dict_aux
    all_bbdd_dictionary = {k: v for element in all_bbdd for k, v in element.items()}
</code>

Para la instalación de esta aplicación necesitamos realizar los siguientes pasos: 

## Descarga y puesta en marcha de manera local

Primeramente, debemos tener instalados en nuestro sistema:

```
python>=3
pypi >=20.17.1 
virtualenv 
```

A continuación se llevará a cabo una explicación de como realizar una puesta en marcha de BIGADATAMED del grupo para poder utilizarla de  manera local para desarrollar las diferentes interfaces de  los proyectos.

Clonación del proyecto
En primer lugar debemos clonar el proyecto que se encuentra en el repositorio http://ugritailab.ugr.es:8000/ugritailab/federamed/bigdatamed mediante la siguiente orden:

```
git clone http://ugritailab.ugr.es:8000/ugritailab/federamed/bigdatamed NombreDelProyectoEnTuMáquinaLocal
```

Una vez tengamos el proyecto clonado en nuestra máquina local pasaremos al siguiente paso que será crear un entorno virtual.

Creación de una rama propia
Cada desarrollador, para cada proyecto deberá de crear una rama propia con el nombre del proyecto y las iniciales del investigador.

```
git checkout -b BIGDATAMED-RMJ
```

IMPORTANTE: Siempre se realizarán todas las actualizaciones locales en la rama del investigador. Posteriormente, si se considera oportuno por el grupo, se actualizará la funcionalidad implementada a  la interfaz genérica del grupo mediante un pull request para verificar la implementación. Con esto se consigue  dar la posiblidad de trabajar sobre una aplicación localmente para cualquier usuario independientemente si  el grupo desea incluir al proyecto genérico  la funcionalidad implementada por el investigador.

Creación entorno virtual
Para crear un entorno virtual necesitaremos ejecutar la siguiente orden:

```
virtalenv nombredelespaciovirtual
```

Para más información sobre virtualenv puedes consultar en su sitio web. https://virtualenv.pypa.io/en/latest/
Una vez creado el entorno virtual, tan solo se necesita activar el entorno de virtual:

```
source venv-bigdatamed/bin/activate
```

IMPORTANTE: El entorno virtual debe empezar por venv* ya que de esta forma el fichero .gitignore ignorará este fichero, ya que, está totalmente prohibido subir este tipo de carpetas. 

Finalmente, pasaremos a instalar los paquetes responsables del correcto funcionamiento de nuestra interfaz.

Instalar paquetes
Para instalar los paquetes necesarios tan solo necesitas ejecutar la siguiente orden:


```
pip3  install -r requirements.txt
``` 



IMPORTANTE: Siempre tener activado el entorno virtual antes de ejecutar este comando.

Ejecutar Django:
Una vez realizado este proceso, ejecuta la siguiente orden en el raíz de nuestra aplicación para comprobar que todo va correctamente.

```
 python manage.py runserver
```

