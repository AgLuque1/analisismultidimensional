# Implementación de un proyecto específico con sus respectivos servicios


Para la implementación del servicio se debe tomar de ejemplo el fichero [service.py] y se estructura en dos bloques:


- La definición de las variables de BluePrint. Framework para que muestre el nombre del proyecto que  engloba los servicios
- La definición de los propios servicios del proyecto.


## Definición de las variables BluePrint
~~~
#  Variable que define Blueprint, esto mostrará en la api el nombre del proyecto
nombre_del_proyecto_bp = Blueprint('nombre del proyecto', __name__)

#  Al ser un componente se debe añadir a la variable global de la api
api = Api( nombre_del_proyecto_bp )

# Se crea una referencia al  spacename  para el proyecto 
ns_nombre_del_proyecto = api.namespace('nombre del proyecto', "Descripción de la API del Proyecto")

~~~


## Definición de los propios servicios
~~~
#   Desccripción principal  del Servicio para Swagger
@ns_nombre_del_proyecto.doc(description="Descripción del Servicio")

#   URL del servicio
@ns_nombre_del_proyecto.route('/',endpoint='Enpoint_Name')

#   Implementación del Servicio
class NombreDelServicio(Resource):
    # Tipo de Servicio: GET,POST,DELETE,UPDATE
    
    def get(self):
        return jsonify({"Hola":"Mundo GET"})
        
    def post(self):
        return jsonify({"Hola":"Mundo POST"})
    
    def put(self):
        return jsonify({"Hola":"Mundo PUT"})
    
    def delete(self):
        return jsonify({"Hola":"Mundo DELETE"})

~~~

Importante: Se puede crear dentro del árbol de carpetas nuevos ficheros de que dependan los servicios principales, que para seguir una sintonía para todos se implementarán en el  fichero service.py

Finalmente, añadir las variables ns_nombre_del_proyecto y nombre_del_proyecto_bp en el archivo, fichero [__init__.py]


[service.py]: https://github.com/ugritlab/API_CLOUDS/blob/main/app/architecture/service.py
[__init__.py]: https://github.com/ugritlab/API_CLOUDS/blob/main/app/__init__.py


~~~

# Añadir variable namespace a nuestra API
api.add_namespace(ns_architecture)
api.add_namespace(ns_energytime)
api.add_namespace(ns_bigdatamed)
api.add_namespace(ns_nombre_del_proyecto)

# Añadir variable blueprint a nuestra API
app.register_blueprint(architecture_bp)
app.register_blueprint(bigdatamed_bp)
app.register_blueprint(energytime_bp)
app.register_blueprint(nombre_del_proyecto_bp)

~~~

El resultado debe ser como muestra la imagen. 


![Ejemplo de como quedaría la API][imgExample]

[imgExample]: /app/img/example-api.png 