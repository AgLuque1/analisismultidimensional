from flask import Flask
from flask_restx import Api, Resource,fields
from .bigdatamed.service       import bigdatamed_bp,ns_bigdatamed
from .energytime.service       import energytime_bp,ns_energytime

from .architecture.service     import architecture_bp,ns_architecture


app = Flask (__name__)


api = Api(app,version="1.0",title="ApiRest UGRITLAB", description="API Rest Grupo Ugritlab",contact="robermorji@ugr.es" )

# Add nameSpace our api
api.add_namespace(ns_architecture)
api.add_namespace(ns_energytime)
api.add_namespace(ns_bigdatamed)

# add blueprint our api
app.register_blueprint(architecture_bp)
app.register_blueprint(bigdatamed_bp)
app.register_blueprint(energytime_bp)






if __name__ == "__main__":
      app.run()

   