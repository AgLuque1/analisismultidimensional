from flask import jsonify
from flask import Blueprint
from flask_restx import Api, Resource,fields,Namespace
from app.lib.database import database as dbases
from bson import json_util
import json

energytime_bp = Blueprint('energytime', __name__)
api = Api( energytime_bp )
ns_energytime = api.namespace('energytime', "Proyect api ENergyTime")


@ns_energytime.doc(description="Nombre de las bases de datos")
@ns_energytime.route('/getDBs',endpoint='getDBsEnergyTime')
class getNameDataBase(Resource):
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer las bases de datos correspondientes
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
    def get(self):
        return jsonify({"Hola":"EnergyTime"})
