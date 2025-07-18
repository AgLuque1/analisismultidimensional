# API CLOUD

## Descarga y puesta en marcha de manera local

Primeramente, debemos tener instalados en nuestro sistema:
~~~
python>=3
pypi >=20.17.1 
virtualenv 
~~~

A continuación se llevará a cabo una explicación de como realizar una puesta en marcha de la ApiRest del grupo para poder utilizarla de  manera local para desarrollar los diferentes proyectos del grupo. 

### Clonación del proyecto
En primer lugar debemos clonar el proyecto que se encuentra en el repositorio https://github.com/ugritlab/API_CLOUDS.git mediante la siguiente orden:

~~~
git clone https://github.com/ugritlab/API_CLOUDS.git NombreDelProyectoEnTuMáquinaLocal
~~~

Una vez tengamos el proyecto clonado en nuestra máquina local pasaremos al siguiente paso que será crear un entorno virtual. 

### Creación de una rama propia
Cada desarrollador, para cada proyecto deberá de crear una rama propia con el nombre del proyecto y las iniciales del investigador.

~~~
git checkout -b BIGDATAMED-RMJ
~~~

IMPORTANTE: Siempre se realizarán todas las actualizaciones locales en la rama del investigador. Posteriormente, si se considera oportuno por el grupo, se actualizará la funcionalidad implementada a  la API genérica del grupo mediante un pull request para verificar la implementación. Con esto se consigue  dar la posiblidad de trabajar sobre una API localmente para cualquier usuario independientemente si  el grupo desea incluir al proyecto genérico del grupo la funcionalidad implementada por el usuario.

### Creación entorno virtual 

Para crear un entorno virtual necesitaremos ejecutar la siguiente orden:

~~~
virtalenv nombredelespaciovirtual
~~~

Para más información sobre virtualenv puedes consultar en su sitio web. https://virtualenv.pypa.io/en/latest/

Una vez creado el entorno virtual, tan solo se necesita activar el entorno de virtual:

~~~
source venv-apicloud/bin/activate
~~~

Finalmente, pasaremos a instalar los paquetes responsables del correcto funcionamiento de nuestra API.  

### Instalar paquetes

Para instalar los paquetes necesarios tan solo necesitas ejecutar la siguiente orden:

~~~
pip3  install -r requirements.txt
~~~

Importante siempre tener activado el entorno virtual antes de ejecutar este comando. 

### Ejecutar FLASK

Una vez realizado este proceso, ejecuta la siguiente orden para comprobar que todo va correctamente.

~~~
flask run
~~~

El resultado mostrado debería ser algo como sigue:

![img]

[img]: img/flask-run.png

[Siguiente Paso]

[Siguiente Paso]: <https://github.com/ugritlab/API_CLOUDS/tree/main/app/architecture>
