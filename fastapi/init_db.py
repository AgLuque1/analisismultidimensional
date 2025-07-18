import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def crear_bds(nombre_bd, user, password, host="localhost", port=5432):
    conn = psycopg2.connect(
        dbname="postgres",  # Conexión a postgres genérica
        user=user,
        password=password,
        host=host,
        port=port
    )
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