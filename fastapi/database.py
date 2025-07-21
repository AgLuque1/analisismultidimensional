from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Conexión bd de modelo
URL_MODELO = 'postgresql://postgres:aaaa@postgres_olap:5432/Modelo_AM'

engine_modelo = create_engine(URL_MODELO)
Session_modelo= sessionmaker(autocommit=False, autoflush=False, bind=engine_modelo)

Modelo = declarative_base()

URL_DATAWAREHOUSE = 'postgresql://postgres:aaaa@postgres_olap:5432/DataWarehouse_AM'

engine_datawarehouse = create_engine(URL_DATAWAREHOUSE)

Session_datawarehouse = sessionmaker(autocommit=False, autoflush=False, bind=engine_datawarehouse)

Datawarehouse = declarative_base()

#Dependencia para obtener la sesión actual del modelo
def get_db_modelo():
    db_modelo = Session_modelo()
    try:
        yield db_modelo
    finally:
        db_modelo.close()

#Dependencia para obtener la sesión actual del datawarehouse
def get_db_datawarehouse():
    db_datawarehouse = Session_datawarehouse()
    try:
        yield db_datawarehouse
    finally:
        db_datawarehouse.close()

        