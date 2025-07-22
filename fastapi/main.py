import init_db
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from routers import api #Importar y agregar routers adicionales a la aplicación
import models
from database import engine_modelo, engine_datawarehouse
from fastapi.middleware.cors import CORSMiddleware

#from sqlalchemy.orm import Session


app = FastAPI()

#Configuración de CORS
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001"
    "http://localhost:8001",
    "http://servicios_olap:8001",  #URL de la aplicación desde donde se realice la llamada
    "http://bigdatamed:8000",  #URL de la aplicación desde donde se realice la llamada
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(api.router)

#models.Base.metadata.create_all(bind=engine_modelo) #crea las tablas en la bd
models.Modelo.metadata.create_all(bind=engine_modelo) #crea las tablas en la bd
#models.Base.metadata.create_all(bind=engine_datawarehouse)
#models.Modelo.metadata.create_all(bind=engine_datawarehouse)


 


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8001)