from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from database import Modelo
import json

class Cubo(Modelo):
    __tablename__ = 'cubos_modelo'

    id = Column(Integer, primary_key=True, index=True)
    propiedades = Column(JSON, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "propiedades": self.propiedades
        }