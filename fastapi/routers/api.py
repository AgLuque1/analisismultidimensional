from fastapi import APIRouter, HTTPException, Depends, Query, Body
from Schema import CuboModeloBase, CuboFilas, CuboDrillDown, CuboRollUp, CuboSlice, CuboInfo, SliceRequest
from database import Session_modelo, get_db_modelo, Session_datawarehouse, get_db_datawarehouse, engine_datawarehouse
from sqlalchemy import Column, Integer, String, Table, MetaData, ForeignKey, inspect, ForeignKeyConstraint, select, text, UniqueConstraint, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Annotated, Dict, Union
import models
import json
import time



router = APIRouter()

#Variable de conexión a la base de datos del modelo
db_modelo_dependency = Annotated[Session_modelo, Depends(get_db_modelo)]

#Variable de conexión a la base de datos de datawarehouse
db_datawarehouse_dependency = Annotated[Session_datawarehouse, Depends(get_db_datawarehouse)]


#Endpoint para obtener los cubos de un usuario
@router.get("/analisismultidimensional/getCubes/{user}")
async def obtenerCubos(user: str, db:db_modelo_dependency):
    #Obtiene los cubos del usuario 'user'
    #cubos = db.query(models.Cubo).filter(json.loads(str(models.Cubo.propiedades))["user"] == user)
    cubos = db.query(models.Cubo).filter(func.json_extract_path_text(models.Cubo.propiedades, 'user') == user)
    #Convertimos los objetos de SQLAlchemy en diccionarios
    cubos_json = [cubo.to_dict() for cubo in cubos]
    return cubos_json

#Endpoint para obtener un cubo dado el nombre del cubo y el usuario
@router.get("/analisismultidimensional/getCube/")
async def obtenerCubo(dbmodel:db_modelo_dependency, user: str = Query(...), nombre_cubo: str = Query(...)):
    username = user
    nombreCubo = nombre_cubo

    cubo = dbmodel.query(models.Cubo).filter(
        func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombreCubo,
        func.json_extract_path_text(models.Cubo.propiedades, 'user') == username
        ).first()
    
    if(cubo):
        cubo_json = cubo.to_dict()
        return cubo_json["propiedades"]
    
    
    raise HTTPException(status_code=404, detail="Cube not found")


#Endpoint para obtener los valores de un nivel de una jerarquia
@router.get("/analisismultidimensional/getLevels/")
async def obtenerNiveles(dbdw: db_datawarehouse_dependency, nombreCubo: str = Query(...), nombreUser: str = Query(...),
                         nombreJerarquia: str = Query(...), nombreNivel: str = Query(...)):
    cubo = nombreCubo
    user = nombreUser
    jerarquia = nombreJerarquia
    nivel = nombreNivel

    #Obtenemos el cubo
    metadatos = MetaData()
    inspector = inspect(engine_datawarehouse)
    nombreTabla = f"{user}_{cubo}_{jerarquia}"

    #Comprobamos que la tabla existe
    if nombreTabla not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail="La tabla no existe")


    tabla = Table(nombreTabla, metadatos, autoload_with=engine_datawarehouse)

    #Verificamos que el nivel está en la tabla
    if nivel not in tabla.columns:
        raise HTTPException(status_code=404, detail="No se encuentra el nivel")

    #Hacemos la consulta
   
    consulta = select(tabla.c[nivel])
    resultados = dbdw.execute(consulta).fetchall()
  
    #Extraemos los valores del resultado
    valores = [resultado[0] for resultado in resultados]

    return {"valores": valores}

    

#Endpoint para guardar la estructura del cubo en la base de datos del modelo
@router.post("/analisismultidimensional/createCubeModel/")
async def crear_cubo_modelo(
    cubo: CuboModeloBase, 
    dbmodel:db_modelo_dependency):

    
    #Verificamos si hay un cubo ya creado con ese nombre por el usuario
    nombre = cubo.propiedades["nombreCubo"]
    usuario = cubo.propiedades["user"]
    
    query = dbmodel.query(models.Cubo).filter(
        func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre,
        func.json_extract_path_text(models.Cubo.propiedades, 'user') == usuario
        ).first()
        

    if(query):
        raise HTTPException(status_code=400, detail="Ya existe un cubo con ese nombre")

    db_cubo = models.Cubo(propiedades = cubo.propiedades)
    dbmodel.add(db_cubo)
    dbmodel.commit()
    dbmodel.refresh(db_cubo)
    print("Este es el modelo: ", cubo)
    return {"detail": "Metadata del cubo creado correctamente en la BD :)"}

@router.post("/analisismultidimensional/createCubeDW/")
async def crear_cubo_dw(
    filas: Dict,
    dbdw:db_datawarehouse_dependency):

    # Definimos metadata
    metadatos = MetaData()

    print("Estas son las filas: ", filas)
    
    dimensiones = filas["estructura"]["dimensiones"]
    filas_datos = filas["datos"]["filas"]
    medida = filas["estructura"]["medida"]
    nombrecubo = filas["estructura"]["nombreCubo"]
    nombreuser = filas["estructura"]["user"]

    print("Filas de datos: ", filas_datos)

    inspector = inspect(engine_datawarehouse)
    
    dimension_tables = {} # Para registrar referencias

    # Primero creamos las tablas de dimensiones
    for dimension, contenido in dimensiones.items():
        tabla_dimension = f"{nombreuser}_{nombrecubo}_{dimension}"
        niveles_total = set()

        '''for jerarquia, jerarquia_data in contenido.get("jerarquias", {}).items():
            niveles = jerarquia_data.get("niveles", [])

            if not isinstance(niveles, list):
                continue

            for nivel in niveles:
                niveles_total.add(nivel)
        '''

        for jerarquia_data in contenido.get("jerarquias", {}).values():
            niveles = jerarquia_data.get("niveles", [])

            if not isinstance(niveles, list):
                continue

            for nivel in niveles:
                niveles_total.add(nivel)

        columnas = [Column(f"{dimension}_id", Integer, primary_key=True, autoincrement=True)]
        for nivel in sorted(niveles_total):  # ordenado por legibilidad
            columnas.append(Column(nivel, String))

        tabla = Table(tabla_dimension, metadatos, *columnas)
        #dimension_tables[jerarquia] = tabla
        jerarquia_por_defecto = contenido.get("jerarquia_por_defecto")
        if jerarquia_por_defecto:
            dimension_tables[dimension] = tabla
        metadatos.create_all(engine_datawarehouse)

    # Creamos la tabla de hechos
    nombre_hechos = f"{nombreuser}_{nombrecubo}_fact"
    columnas_hechos = [Column("id", Integer, primary_key=True, autoincrement=True)]
    claves_foraneas = []
    columnas_unicas = []

    for dimension in dimensiones:
        columnas_hechos.append(Column(f"{dimension}_id", Integer))
        claves_foraneas.append(
            ForeignKeyConstraint(
                [f"{dimension}_id"],
                [f"{nombreuser}_{nombrecubo}_{dimension}.{dimension}_id"]
            )
        )
        columnas_unicas.append(f"{dimension}_id")

    columnas_hechos.append(Column(medida, Integer))
    tabla_hechos = Table(nombre_hechos, metadatos, *columnas_hechos, *claves_foraneas, UniqueConstraint(*columnas_unicas))
    metadatos.create_all(engine_datawarehouse)

    # Insertamos los datos
    for fila in filas_datos:
        ids_jerarquias = {}

        for dimension, contenido in dimensiones.items():
            jerarquia_defecto = contenido.get("jerarquia_por_defecto")
            jerarquias = contenido.get("jerarquias", {})

            for jerarquia, jerarquia_data in jerarquias.items():
                niveles = jerarquia_data.get("niveles", [])

                if not isinstance(niveles, list):
                    continue

                #tabla_dim = dimension_tables[jerarquia] 
                tabla_dim = dimension_tables[dimension] 
                
                valores_dim = {
                    nivel: str(fila[nivel])
                    for nivel in niveles
                }

                columnas_select = [tabla_dim.c[f"{dimension}_id"]] + [
                    tabla_dim.c[k] for k in valores_dim.keys()
                ]

                # Verificamos que no se inserten datos duplicados en las tablas
                sel = select(*columnas_select).filter_by(**valores_dim)
                result = dbdw.execute(sel).mappings().fetchone()

                if result:
                    dim_id = result[f"{dimension}_id"]
                else:
                    ins = tabla_dim.insert().values(**valores_dim)
                    result = dbdw.execute(ins)
                    dbdw.commit()
                    dim_id = result.inserted_primary_key[0]

                # Guardamos solo la jerarquía por defecto para la tabla de hechos
                if jerarquia == jerarquia_defecto:
                    ids_jerarquias[dimension] = dim_id

        # Insertarmos los valores en la tabla de hechos
        valores_hechos = {
            f"{dimension}_id": ids_jerarquias[dimension]
            for dimension in ids_jerarquias
        }
        valores_hechos[medida] = fila[medida]

        ins_hechos = tabla_hechos.insert().values(**valores_hechos)
        try:
            dbdw.execute(ins_hechos)
            dbdw.commit()
        except SQLAlchemyError as e:
            print(f"Error insertando en tabla de hechos: {e}")
            raise HTTPException(status_code=500, detail=f"Error insertando en hechos: {e}")


    return {"message": "Modelo del cubo creado correctamente en la BD :)"}
    
#Endpoint para borrar un cubo dado su nombre
@router.delete("/analisismultidimensional/deleteCube/")
async def borrar_cubo(dbmodel:db_modelo_dependency, dbdw:db_datawarehouse_dependency, 
                      user: str = Query(...), nombre_cubo: str = Query(...)):
    #Primero comprobamos que el cubo existe

    cubo = dbmodel.query(models.Cubo).filter(
        func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
        func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()

    if not cubo:
        raise HTTPException(status_code=404, detail="Cubo no encontrado")
    
  

    #Ahora vamos a generar los nombres de las tablas que se 
    #han creado en la bd de datawarehouse para su eliminacion

    dimensiones = cubo.propiedades["dimensiones"]
    print("Estas son las dimensiones")
    for dimension in dimensiones:
        print(dimension)

    nombre_base = f"{user}_{nombre_cubo}"
    nombre_tabla_hechos = f"{nombre_base}_fact"

    tablas_dimensiones = [
        f"{nombre_base}_{dimension}"
        for dimension in dimensiones
    ]

    #Función para escapar los nombres de las tablas y evitar
    #errores de sintaxis, por ejemplo con los espacios
    def escapar_nombre_tabla(tabla):
        return f'"{tabla}"'

    #Borramos primero la tabla de hechos
    with db_datawarehouse_dependency.begin() as connection:
        connection.execute(text(f"DROP TABLE IF EXISTS {escapar_nombre_tabla(nombre_tabla_hechos)} CASCADE"))

        #Ahora borramos las tablas de dimensiones
        for tabla in tablas_dimensiones:
            connection.execute(text(f"DROP TABLE IF EXISTS {escapar_nombre_tabla(tabla)} CASCADE"))

    #Ahora borramos el registro del cubo de la base de datos del modelo
    dbmodel.delete(cubo)
    dbmodel.commit()


    return {"message": "Cubo borrado correctamente"}

#---------OPERACIONES-------



#Endpoint para realizar la operacion roll up, subiendo al siguiente nivel
@router.post("/analisismultidimensional/rollup/")
async def rollup(
    dbdw:db_datawarehouse_dependency, 
    dbmodel:db_modelo_dependency,
    user: str = Query(...),
    nombre_cubo: str = Query(...),
    dimension: str = Query(...),
    medida: str = Query(...),
    nivel_destino: str = Query(...),
    operacion: str = Query("SUM"),
    ):

    try:

        print("Operacion: ", operacion)
        # Validaciones
        operacion = operacion.upper()
        if operacion not in {"SUM", "AVG", "MIN", "MAX"}:
            raise HTTPException(status_code=400, detail="Operación no válida")
        
        # Extraemos el cubo primero
        cubo = dbmodel.query(models.Cubo).filter(
        func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
        func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()

        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")
         
        propiedades = cubo.propiedades

        dimensiones = propiedades.get("dimensiones", {})

        if (dimension not in dimensiones):
            raise HTTPException(status_code=400, detail="Dimensión no encontrada")
        
        jerarquia_defecto = dimensiones[dimension]["jerarquia_por_defecto"]
        jerarquia = dimensiones[dimension]["jerarquias"].get(jerarquia_defecto, {})
        niveles = jerarquia.get("niveles", [])
        nivel_actual = jerarquia.get("nivel_actual");

        if (nivel_destino not in niveles):
             raise HTTPException(status_code=400, detail="El nivel destino no existe en la jerarquía")

        if (not nivel_actual or nivel_actual not in niveles):
            raise HTTPException(status_code=400, detail="El nivel actual no pertenece a la dimensión")
        
        idx_actual = niveles.index(nivel_actual)
        idx_destino = niveles.index(nivel_destino)
 
        if (idx_destino >= idx_actual):
            raise HTTPException(status_code=400, detail="El nivel destino no es más general")
        
        nombre_tabla_hechos = f"{user}_{nombre_cubo}_fact"
        nombre_tabla_dimension = f"{user}_{nombre_cubo}_{dimension}"

        query = text(f"""
            SELECT d.{nivel_destino} AS agrupado_por, {operacion}(f.{medida}) AS total
            FROM "{nombre_tabla_hechos}" f
            JOIN "{nombre_tabla_dimension}" d
            ON f.{dimension}_id = d.{dimension}_id
            GROUP BY d.{nivel_destino}
            ORDER BY d.{nivel_destino}
        """)       

        result = dbdw.execute(query).fetchall() 

        datos = [{"nivel": fila[0], "valor": fila[1]} for fila in result]


        # Actualizamos el nivel en el modelo
        jerarquia["nivel_actual"] = nivel_destino
        flag_modified(cubo, "propiedades")
        dbmodel.commit()

        return {
        "operacion": "rollup",
        "dimension": dimension,
        "agrupado_por": nivel_destino,
        "tipo_agregacion": operacion,
        "datos": datos
        }
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en rollup: {str(e)}")



#Endpoint para realizar la operacion drill down, bajando al siguiente nivel
@router.post("/analisismultidimensional/drilldown/")
async def drilldown(
    dbdw: db_datawarehouse_dependency,
    dbmodel: db_modelo_dependency,
    user: str = Query(...),
    nombre_cubo: str = Query(...),
    dimension: str = Query(...),
    medida: str = Query(...),
    nivel_destino: str = Query(...),
    operacion: str = Query("SUM")
):
    try:

        operacion = operacion.upper()
        if operacion not in {"SUM", "AVG", "MIN", "MAX"}:
            raise HTTPException(status_code=400, detail="Operación no válida")

        # Recuperar el cubo desde la BD de modelos
        cubo = dbmodel.query(models.Cubo).filter(
            func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
            func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()

        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")

        dimensiones = cubo.propiedades.get("dimensiones", {})

        if (dimension not in dimensiones):
            raise HTTPException(status_code=400, detail="Dimensión no encontrada")
        
        jerarquia_defecto = dimensiones[dimension]["jerarquia_por_defecto"]
        jerarquia = dimensiones[dimension]["jerarquias"].get(jerarquia_defecto, {})
        niveles = jerarquia.get("niveles", [])
        nivel_actual = jerarquia.get("nivel_actual")

        print("Niveles de la dimension")
        for nivel in niveles:
            print(nivel)
        print("Nivel actual es: ", nivel_actual)

        if not nivel_actual or nivel_actual not in niveles:
            raise HTTPException(status_code=400, detail="El nivel no pertenece a la dimensión")
        
        if (nivel_destino not in niveles):
             raise HTTPException(status_code=400, detail="El nivel destino no existe en la jerarquía")
        
        idx_actual = niveles.index(nivel_actual)
        idx_destino = niveles.index(nivel_destino)

        if (idx_destino <= idx_actual):
            raise HTTPException(status_code=400, detail="El nivel destino no es más especifico")

        nombre_tabla_hechos = f"{user}_{nombre_cubo}_fact"
        nombre_tabla_dimension = f"{user}_{nombre_cubo}_{dimension}"

        query = text(f"""
            SELECT d.{nivel_destino} AS agrupado_por, {operacion}(f.{medida}) AS total
            FROM "{nombre_tabla_hechos}" f
            JOIN "{nombre_tabla_dimension}" d
            ON f.{dimension}_id = d.{dimension}_id
            GROUP BY d.{nivel_destino}
            ORDER BY d.{nivel_destino}
        """)

        result = dbdw.execute(query).fetchall()
        datos = [{"nivel": fila[0], "valor": fila[1]} for fila in result]

        # Actualizamos el nivel_actual en el modelo
        jerarquia["nivel_actual"] = nivel_destino
        flag_modified(cubo, "propiedades")
        dbmodel.commit()

        return {
            "operacion": "drilldown",
            "dimension": dimension,
            "agrupado_por": nivel_destino,
            "tipo_agregacion": operacion,
            "datos": datos
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en drilldown: {str(e)}")


#Endpoint para realizar la operacion slice
#Se fija el valor de una dimensión, se filtra por eso.


#Nuevo slice
@router.post("/analisismultidimensional/slice/")
async def slice_dimension(
    dbdw: db_datawarehouse_dependency,
    dbmodel: db_modelo_dependency,
    payload: SliceRequest
    
):
    try:
        print("Dentro de slice2")
        operacion = payload.operacion.upper()
        if operacion not in {"SUM", "AVG", "MIN", "MAX"}:
            raise HTTPException(status_code=400, detail="Operación no válida")

        cubo = dbmodel.query(models.Cubo).filter(
            func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == payload.nombre_cubo,
            func.json_extract_path_text(models.Cubo.propiedades, 'user') == payload.user
        ).first()

        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")

        dimensiones_modelo = cubo.propiedades.get("dimensiones", {})

        if len(payload.dimensiones) != 2:
            raise HTTPException(status_code=400, detail="Debes seleccionar exactamente 2 dimensiones")

        for dim in payload.dimensiones:
            if dim not in dimensiones_modelo:
                raise HTTPException(status_code=400, detail=f"Dimensión {dim} no válida")

        tabla_hechos = f"{payload.user}_{payload.nombre_cubo}_fact"
        joins = []
        select_cols = []
        group_by_cols = []

        for dim in payload.dimensiones:
            tabla_dim = f"{payload.user}_{payload.nombre_cubo}_{dim}"
            alias = f"dim_{dim}"
            jerarquia = dimensiones_modelo[dim]["jerarquias"][dimensiones_modelo[dim]["jerarquia_por_defecto"]]
            nivel_actual = jerarquia.get("nivel_actual") or jerarquia["niveles"][-1]

            joins.append(f'JOIN "{tabla_dim}" {alias} ON f.{dim}_id = {alias}.{dim}_id')
            select_cols.append(f'{alias}.{nivel_actual} AS {dim}_{nivel_actual}')
            group_by_cols.append(f'{alias}.{nivel_actual}')

        select_cols.append(f"{operacion}(f.{payload.medida}) AS total")

        query = f'''
            SELECT {', '.join(select_cols)}
            FROM "{tabla_hechos}" f
            {' '.join(joins)}
            GROUP BY {', '.join(group_by_cols)}
            ORDER BY {', '.join(group_by_cols)}
        '''

        result = dbdw.execute(text(query)).fetchall()
        columnas = [col.split(" AS ")[-1] for col in select_cols if " AS " in col] + ["total"]
        datos = [dict(zip(columnas, row)) for row in result]

        return {
            "operacion": "slice",
            "dimensiones_mantenidas": payload.dimensiones,
            "tipo_agregacion": operacion,
            "datos": datos
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en slice: {str(e)}")


#Endpoint para realizar la operacion dice
@router.post("/analisismultidimensional/dice/")
async def dice(
    dbdw:db_datawarehouse_dependency, 
    dbmodel:db_modelo_dependency,
    user: str = Query(...),
    nombre_cubo: str = Query(...),
    medida: str = Query(...),
    operacion: str = Query("SUM"),
    condiciones: Dict[str, str] = Body(...)
    ):
   
    try:

        if len(condiciones) < 2:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos dos condiciones para dice")
    
        if len(condiciones) == 3:
            operacion = "SUM"  # Forzamos SUM porque no tiene sentido AVG/MIN/MAX con un único valor

        # Cargar el modelo del cubo
        cubo = dbmodel.query(models.Cubo).filter(
            func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
            func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()

        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")
        
       
        dimensiones = cubo.propiedades.get("dimensiones", {})

        tabla_hechos = f"{user}_{nombre_cubo}_fact"
        condiciones_sql = []
        params = {}
        
        # Comprobamos las condiciones y preparamos los joins
        joins = []
        alias_map = {}
        for i, (dimension, valor) in enumerate(condiciones.items()):
            if dimension not in dimensiones:
                raise HTTPException(status_code=400, detail=f"Dimensión {dimension} no encontrada")

            tabla_dim = f"{user}_{nombre_cubo}_{dimension}"
            alias = f"d{i}"
            alias_map[dimension] = alias
            joins.append(f"JOIN \"{tabla_dim}\" {alias} ON f.{dimension}_id = {alias}.{dimension}_id")

            # Verificamos si el valor existe en alguna columna (nivel) de la tabla
            # Si existe, metemos la dimension y el valor en condiciones y params
            jerarquia_defecto = dimensiones[dimension]["jerarquia_por_defecto"]
            niveles = dimensiones[dimension]["jerarquias"][jerarquia_defecto]["niveles"]
            encontrado = False
            for nivel in niveles:
                query = text(f"SELECT 1 FROM \"{tabla_dim}\" WHERE {nivel} = :valor LIMIT 1")
                result = dbdw.execute(query, {"valor": valor}).fetchone()
                if result:
                    condiciones_sql.append(f"{alias}.{nivel} = :{dimension}")
                    params[dimension] = valor
                    encontrado = True
                    break

            if not encontrado:
                raise HTTPException(status_code=400, detail=f"Valor {valor} no encontrado en niveles de {dimension}")

        # Si el cubo tiene 3 dimensiones y solo se proporcionan 2 valores, se tiene que agrupar por el 
        # nivel actual de la dimensión que no se ha especificado valor
        if len(condiciones) == 2 and len(dimensiones) == 3:
            dimension_faltante = next(d for d in dimensiones if d not in condiciones)
            jerarquia_defecto = dimensiones[dimension_faltante]["jerarquia_por_defecto"]
            nivel_actual = dimensiones[dimension_faltante]["jerarquias"][jerarquia_defecto].get("nivel_actual")
            if not nivel_actual:
                nivel_actual = dimensiones[dimension_faltante]["jerarquias"][jerarquia_defecto]["niveles"][-1]

            tabla_dim = f"{user}_{nombre_cubo}_{dimension_faltante}"
            alias = dimension_faltante
            joins.append(f"JOIN \"{tabla_dim}\" {alias} ON f.{dimension_faltante}_id = {alias}.{dimension_faltante}_id")
            group_by = f"{alias}.{nivel_actual}"
            select_col = f"{alias}.{nivel_actual} AS agrupado_por"
        # Si se han dado los 3 valores de dimensiones, no se hace group by
        else:
            group_by = None
            select_col = ""

        # select_col es la columna por la que se agrupará en caso de haber dado 2 valores de dimensiones
        select = f"{select_col}, " if select_col else ""
        query_sql = f"""
            SELECT {select}{operacion}(f.{medida}) AS total
            FROM "{tabla_hechos}" f
            {' '.join(joins)}
            WHERE {' AND '.join(condiciones_sql)}
            {f'GROUP BY {group_by}' if group_by else ''}
            {f'ORDER BY {group_by}' if group_by else ''}
        """

        result = dbdw.execute(text(query_sql), params).fetchall()

        if group_by:
            agrupado_por = group_by.split(".")[-1]
            datos = [{"nivel": row[0], "valor": row[1]} for row in result]
        else:
            total = result[0][0] if result else 0
            print("Dentro del else, se proporcionaron 3 valores, el resultado es: ", total)
            datos = {"total": total}
             # Si no hay group_by (es decir, se han dado los 3 valores), generamos una etiqueta combinada
            agrupado_por = " - ".join([f"{k}: {v}" for k, v in condiciones.items()])
            print("Agrupado por: ", agrupado_por)

        return {
            "operacion": "dice",
            "condiciones": condiciones,
            "agrupado_por": agrupado_por,
            "resultado": datos
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en dice: {str(e)}")

'''
#Endpoint para realizar la operacion dice
@router.post("/analisismultidimensional/dice2/")
async def dice2(
    dbdw: db_datawarehouse_dependency,
    dbmodel: db_modelo_dependency,
    user: str = Query(...),
    nombre_cubo: str = Query(...),
    medida: str = Query(...),
    operacion: str = Query("SUM"),
    condiciones: List[Dict[str, Union[str, Dict[str, str]]]] = Body(...)
):
    
    """
    condiciones: una lista de condiciones, cada una con una estructura como:
    {
      "operador": "AND" / "OR",
      "condiciones": {
        "dimension": "valor",
        "otra_dimension": "valor"
      }
    }
    """
    try:
        cubo = dbmodel.query(models.Cubo).filter(
            func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
            func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()

        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")

        dimensiones = cubo.propiedades.get("dimensiones", {})
        tabla_hechos = f"{user}_{nombre_cubo}_fact"
        joins = []
        where_parts = []
        params = {}

        alias_map = {}
        alias_count = 0

        for grupo in condiciones:
            op = grupo.get("operador", "AND").upper()
            if op not in {"AND", "OR"}:
                raise HTTPException(status_code=400, detail="Operador no válido")

            cond_parts = []
            for dimension, valor in grupo["condiciones"].items():
                if dimension not in dimensiones:
                    raise HTTPException(status_code=400, detail=f"Dimensión {dimension} no encontrada")

                tabla_dim = f"{user}_{nombre_cubo}_{dimension}"
                if dimension not in alias_map:
                    alias = f"d{alias_count}"
                    joins.append(f'JOIN "{tabla_dim}" {alias} ON f.{dimension}_id = {alias}.{dimension}_id')
                    alias_map[dimension] = alias
                    alias_count += 1
                else:
                    alias = alias_map[dimension]

                jerarquia_defecto = dimensiones[dimension]["jerarquia_por_defecto"]
                niveles = dimensiones[dimension]["jerarquias"][jerarquia_defecto]["niveles"]
                encontrado = False
                for nivel in niveles:
                    query = text(f'SELECT 1 FROM "{tabla_dim}" WHERE {nivel} = :valor LIMIT 1')
                    result = dbdw.execute(query, {"valor": valor}).fetchone()
                    if result:
                        param_key = f"{dimension}_{nivel}_{len(params)}"
                        cond_parts.append(f'{alias}.{nivel} = :{param_key}')
                        params[param_key] = valor
                        encontrado = True
                        break
                if not encontrado:
                    raise HTTPException(status_code=400, detail=f"Valor {valor} no encontrado para {dimension}")

            where_parts.append(f"({f' {op} '.join(cond_parts)})")

        final_where = ' AND '.join(where_parts)
  
        result = dbdw.execute(text(query_sql), params).fetchone()
        total = result[0] if result else 0

        return {
            "operacion": "dice_logico",
            "condiciones": condiciones,
            "tipo_agregacion": operacion,
            "resultado": total
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en dice_logico: {str(e)}")
''' 

@router.post("/analisismultidimensional/getDatosCubo/")
async def resumen_cubo_actual(
    dbdw: db_datawarehouse_dependency,
    dbmodel: db_modelo_dependency,
    user: str = Query(...),
    nombre_cubo: str = Query(...),
    medida: str = Query(...),
    operacion: str = Query("SUM")
):
    try:

        operacion = operacion.upper()
        if operacion not in {"SUM", "AVG", "MIN", "MAX"}:
            raise HTTPException(status_code=400, detail="Operación no válida")

        # Buscar el cubo
        cubo = dbmodel.query(models.Cubo).filter(
            func.json_extract_path_text(models.Cubo.propiedades, 'nombreCubo') == nombre_cubo,
            func.json_extract_path_text(models.Cubo.propiedades, 'user') == user
        ).first()
        
        if not cubo:
            raise HTTPException(status_code=404, detail="Cubo no encontrado")

        propiedades = cubo.propiedades
        dimensiones = propiedades.get("dimensiones", {})

        nombre_tabla_hechos = f"{user}_{nombre_cubo}_fact"
        resultados = {}

        for dimension, info in dimensiones.items():
            jerarquia = info["jerarquias"][info["jerarquia_por_defecto"]]
            nivel_actual = jerarquia.get("nivel_actual") or jerarquia["niveles"][-1]
            tabla_dimension = f"{user}_{nombre_cubo}_{dimension}"

            query = text(f"""
                SELECT d.{nivel_actual} AS agrupado_por, {operacion}(f.{medida}) AS total
                FROM "{nombre_tabla_hechos}" f
                JOIN "{tabla_dimension}" d
                ON f.{dimension}_id = d.{dimension}_id
                GROUP BY d.{nivel_actual}
                ORDER BY d.{nivel_actual}
            """)

            result = dbdw.execute(query).fetchall()
            resultados[dimension] = [{"nivel": row[0], "valor": row[1]} for row in result]

        return {
            "operacion": "get_datos_cubo",
            "tipo_agregacion": operacion,
            "dimension_niveles_actuales": {dim: info["jerarquias"][info["jerarquia_por_defecto"]].get("nivel_actual") for dim, info in dimensiones.items()},
            "datos": resultados
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen: {str(e)}")
  
