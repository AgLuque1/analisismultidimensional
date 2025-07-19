import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

def crear_bds(nombre_bd, user, password, host="127.0.0.1", port=5432):
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            break
        except Exception as e:
            print("Esperando POSTGRESQL.. {e}")
            time.sleep(2)

    else:
        raise Exception ("No se pudo conectar a postgresql")

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nombre_bd,))
    existe = cursor.fetchone()

    if not existe:
        cursor.execute(f'CREATE DATABASE "{nombre_bd}"')
        print(f"Base de datos '{nombre_bd}' creada.")
    else:
        print(f"La base de datos '{nombre_bd}' ya existe.")

    cursor.close()
    conn.close()

crear_bds("Modelo_AM", user="postgres", password="aaaa")
crear_bds("DataWarehouse_AM", user="postgres", password="aaaa")
