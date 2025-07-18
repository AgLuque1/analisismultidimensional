from pydantic import BaseModel   #Para data validation
from typing import Dict, List

#Clase para validación
class CuboModeloBase(BaseModel):
    propiedades: Dict

    class Config:
        orm_mode = True

class CuboFilas(BaseModel):
    filas: Dict

    class Config:
        orm_mode = True

class CuboDrillDown(BaseModel):
    propiedades: Dict
    dimension: str
    jerarquia_especifica: str

    class Config:
        orm_mode = True

class CuboRollUp(BaseModel):
    propiedades: Dict

    class Config:
        orm_mode = True

class CuboSlice(BaseModel):
    propiedades: Dict
    dimension: str
    jerarquia: str
    nivel: str
    valor_nivel: str
    nombreNuevoCubo: str

    class Config:
        orm_mode = True

class CuboInfo(BaseModel):
    user: str
    nombre_cubo: str

class SliceRequest(BaseModel):
    user: str
    nombre_cubo: str
    dimensiones: List[str]
    medida: str
    operacion: str = "SUM"