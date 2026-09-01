"""
Módulo de consultas (CRUD) para estudiantes y atenciones.
"""

import uuid
from datetime import datetime
from database.modelos import conectar
from config import obtener_origen_pc

# ==========================================================
# ESTUDIANTES
# ==========================================================

def crear_estudiante(nombre, curso, paralelo=None, sexo=None):
    """Inserta un nuevo estudiante. Devuelve el id (UUID) generado."""
    id_estudiante = str(uuid.uuid4())
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO estudiantes (id, nombre, curso, paralelo, sexo, origen_pc)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_estudiante, nombre, curso, paralelo, sexo, obtener_origen_pc()))

    conexion.commit()
    conexion.close()
    return id_estudiante

def buscar_estudiantes_por_nombre(texto_busqueda, limite=8):
    """Busca estudiantes cuyo nombre contenga el texto dado (para autocompletado)."""
    if not texto_busqueda:
        return []
    conexion = conectar()
    cursor = conexion.cursor()
    patron = f"%{texto_busqueda}%"
    cursor.execute("""
        SELECT id, nombre, curso, paralelo, sexo FROM estudiantes
        WHERE nombre LIKE ?
        ORDER BY nombre
        LIMIT ?
    """, (patron, limite))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def buscar_estudiante_exacto(nombre, curso, paralelo):
    """Busca coincidencia exacta de nombre + curso + paralelo (para evitar duplicados al crear)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id FROM estudiantes
        WHERE LOWER(nombre) = LOWER(?) AND curso = ? AND IFNULL(paralelo, '') = IFNULL(?, '')
    """, (nombre.strip(), curso, paralelo))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None

def listar_todas_atenciones():
    """Devuelve el historial completo de atenciones (todas las fechas), más reciente primero."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.*, e.nombre, e.curso, e.paralelo, e.sexo
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        ORDER BY a.fecha DESC, a.hora_llegada DESC
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def filtrar_atenciones(texto_busqueda):
    """Filtra el historial por nombre, curso, paralelo o diagnóstico."""
    if not texto_busqueda:
        return listar_todas_atenciones()

    conexion = conectar()
    cursor = conexion.cursor()
    patron = f"%{texto_busqueda}%"
    cursor.execute("""
        SELECT a.*, e.nombre, e.curso, e.paralelo, e.sexo
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE e.nombre LIKE ? OR e.curso LIKE ? OR e.paralelo LIKE ? OR a.diagnostico LIKE ?
        ORDER BY a.fecha DESC, a.hora_llegada DESC
    """, (patron, patron, patron, patron))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def actualizar_estudiante(id_estudiante, nombre, curso, paralelo, sexo):
    """Actualiza los datos de un estudiante existente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE estudiantes
        SET nombre = ?, curso = ?, paralelo = ?, sexo = ?
        WHERE id = ?
    """, (nombre, curso, paralelo, sexo, id_estudiante))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    return filas_afectadas > 0

def obtener_estudiante_por_id(id_estudiante):
    """Devuelve la fila completa de un estudiante según su id, o None si no existe."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estudiantes WHERE id = ?", (id_estudiante,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

# ==========================================================
# ATENCIONES
# ==========================================================

def crear_atencion(estudiante_id, saturacion=None, temperatura=None,
                    frecuencia_cardiaca=None, diagnostico=None, recomendacion=None,
                    hora_llegada=None, fecha=None, enfermera_responsable=None):
    """Registra una nueva atención de enfermería. Devuelve el id (UUID) generado."""
    id_atencion = str(uuid.uuid4())
    fecha = fecha or datetime.now().strftime("%Y-%m-%d")
    hora_llegada = hora_llegada or datetime.now().strftime("%H:%M:%S")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO atenciones (
            id, estudiante_id, fecha, hora_llegada, saturacion, temperatura,
            frecuencia_cardiaca, diagnostico, recomendacion,
            enfermera_responsable, origen_pc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_atencion, estudiante_id, fecha, hora_llegada, saturacion, temperatura,
        frecuencia_cardiaca, diagnostico, recomendacion,
        enfermera_responsable, obtener_origen_pc()
    ))

    conexion.commit()
    conexion.close()
    return id_atencion

def cerrar_atencion(id_atencion, hora_salida=None):
    """Registra la hora de salida de una atención (cuando el estudiante se retira)."""
    hora_salida = hora_salida or datetime.now().strftime("%H:%M:%S")
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE atenciones SET hora_salida = ? WHERE id = ?", (hora_salida, id_atencion))
    conexion.commit()
    conexion.close()


def listar_atenciones_por_fecha(fecha):
    """Devuelve todas las atenciones de una fecha específica (formato YYYY-MM-DD)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.*, e.nombre, e.curso, e.paralelo, e.sexo
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE a.fecha = ?
        ORDER BY a.hora_llegada
    """, (fecha,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def actualizar_atencion(id_atencion, saturacion, temperatura, frecuencia_cardiaca, diagnostico, recomendacion):
    """Actualiza los datos clínicos de una atención existente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE atenciones
        SET saturacion = ?, temperatura = ?, frecuencia_cardiaca = ?, diagnostico = ?, recomendacion = ?
        WHERE id = ?
    """, (saturacion, temperatura, frecuencia_cardiaca, diagnostico, recomendacion, id_atencion))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    return filas_afectadas > 0

def eliminar_atencion(id_atencion):
    """Elimina una atención específica (no afecta al estudiante en el catálogo)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM atenciones WHERE id = ?", (id_atencion,))
    conexion.commit()
    conexion.close()

def listar_atenciones_pendientes():
    """
    Devuelve todas las atenciones (de cualquier fecha) que aún no tienen
    hora de salida registrada. Ordenadas de la más antigua a la más reciente,
    para que las pendientes más urgentes aparezcan primero.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.*, e.nombre, e.curso, e.paralelo, e.sexo
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE a.hora_salida IS NULL
        ORDER BY a.fecha ASC, a.hora_llegada ASC
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

# ==========================================================
# GRAFICAS -  REPORTES
# ==========================================================

def listar_meses_disponibles():
    """Devuelve los meses (YYYY-MM) que tienen atenciones registradas, más reciente primero."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT DISTINCT strftime('%Y-%m', fecha) AS mes
        FROM atenciones
        ORDER BY mes DESC
    """)
    resultados = [fila[0] for fila in cursor.fetchall()]
    conexion.close()
    return resultados


def contar_atenciones_por_mes():
    """Devuelve (mes, total) de TODOS los meses con datos, ordenado cronológicamente (para la tendencia)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', fecha) AS mes, COUNT(*) AS total
        FROM atenciones
        GROUP BY mes
        ORDER BY mes ASC
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def contar_diagnosticos_por_mes(mes, diagnosticos_predefinidos, limite=8):
    """Devuelve (diagnostico, total) del mes indicado, los más frecuentes primero."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    placeholders = ",".join("?" for _ in diagnosticos_predefinidos)
    cursor.execute(f"""
        SELECT
            CASE
                WHEN diagnostico IN ({placeholders}) THEN diagnostico
                ELSE 'Otros'
            END AS diagnostico_agrupado,
            COUNT(*) AS total
        FROM atenciones
        WHERE strftime('%Y-%m', fecha) = ?
        GROUP BY diagnostico_agrupado
        ORDER BY total DESC
        LIMIT ?
    """, (*diagnosticos_predefinidos, mes, limite))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def contar_atenciones_por_curso_mes(mes):
    """Devuelve (curso, total) del mes indicado, agrupado por curso."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.curso, COUNT(*) AS total
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE strftime('%Y-%m', a.fecha) = ?
        GROUP BY e.curso
    """, (mes,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def contar_atenciones_por_especialidad_mes(mes):
    """Devuelve (curso, paralelo, total) del mes, agrupado por curso Y paralelo.
    Se usa para desglosar Bachillerato por especialidad, ya que la especialidad
    vive en el campo 'paralelo', no en 'curso'."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.curso, e.paralelo, COUNT(*) AS total
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE strftime('%Y-%m', a.fecha) = ?
        GROUP BY e.curso, e.paralelo
    """, (mes,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def contar_atenciones_por_mes_filtrado(curso, paralelo):
    """Tendencia mensual de atenciones para un curso+paralelo específico."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', a.fecha) AS mes, COUNT(*) AS total
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE e.curso = ? AND e.paralelo = ?
        GROUP BY mes
        ORDER BY mes ASC
    """, (curso, paralelo))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def contar_diagnosticos_por_mes_filtrado(mes, curso, paralelo, diagnosticos_predefinidos, limite=8):
    """Diagnósticos más frecuentes de un curso+paralelo específico, en un mes dado.
    Igual que contar_diagnosticos_por_mes, pero además filtrado por curso/paralelo."""
    conexion = conectar()
    cursor = conexion.cursor()

    placeholders = ",".join("?" for _ in diagnosticos_predefinidos)
    cursor.execute(f"""
        SELECT
            CASE
                WHEN a.diagnostico IN ({placeholders}) THEN a.diagnostico
                ELSE 'Otros'
            END AS diagnostico_agrupado,
            COUNT(*) AS total
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE strftime('%Y-%m', a.fecha) = ? AND e.curso = ? AND e.paralelo = ?
        GROUP BY diagnostico_agrupado
        ORDER BY total DESC
        LIMIT ?
    """, (*diagnosticos_predefinidos, mes, curso, paralelo, limite))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

# ==========================================================
# EXPORTACION / SINCRONIZACION DE DATOS 
# ==========================================================

def exportar_datos_mes(mes):
    """
    Devuelve (estudiantes, atenciones) de un mes específico, listos para exportar.
    Solo incluye los estudiantes que tienen al menos una atención en ese mes
    (para no exportar el catálogo completo innecesariamente).
    """
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, estudiante_id, fecha, hora_llegada, hora_salida, saturacion,
            temperatura, frecuencia_cardiaca, diagnostico, recomendacion,
            enfermera_responsable, origen_pc, fecha_registro
        FROM atenciones
        WHERE strftime('%Y-%m', fecha) = ?
    """, (mes,))
    columnas_atencion = [d[0] for d in cursor.description]
    atenciones = [dict(zip(columnas_atencion, fila)) for fila in cursor.fetchall()]

    ids_estudiantes = list({a["estudiante_id"] for a in atenciones})
    estudiantes = []
    if ids_estudiantes:
        placeholders = ",".join("?" for _ in ids_estudiantes)
        cursor.execute(f"""
            SELECT id, nombre, curso, paralelo, sexo, origen_pc, fecha_creacion
            FROM estudiantes
            WHERE id IN ({placeholders})
        """, ids_estudiantes)
        columnas_est = [d[0] for d in cursor.description]
        estudiantes = [dict(zip(columnas_est, fila)) for fila in cursor.fetchall()]

    conexion.close()
    return estudiantes, atenciones

# ==========================================================
# IMPORTACIÓN / SINCRONIZACIÓN
# ==========================================================

def existe_estudiante_id(id_estudiante):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM estudiantes WHERE id = ?", (id_estudiante,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None

def insertar_estudiante_con_id(id_estudiante, nombre, curso, paralelo, sexo, origen_pc, fecha_creacion):
    """Inserta un estudiante preservando su id original (usado al importar)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO estudiantes (id, nombre, curso, paralelo, sexo, origen_pc, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (id_estudiante, nombre, curso, paralelo, sexo, origen_pc, fecha_creacion))
    conexion.commit()
    conexion.close()


def existe_atencion_id(id_atencion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM atenciones WHERE id = ?", (id_atencion,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None


def buscar_atenciones_similares(estudiante_id, fecha, hora_llegada, ventana_minutos=15):
    """
    Busca atenciones YA EXISTENTES en la BD local para el mismo estudiante y fecha,
    con hora de llegada dentro de una ventana de minutos. Se usa para detectar
    posibles duplicados al importar (misma visita registrada por error en ambas PCs).
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, hora_llegada, diagnostico, origen_pc
        FROM atenciones
        WHERE estudiante_id = ? AND fecha = ?
    """, (estudiante_id, fecha))
    resultados = cursor.fetchall()
    conexion.close()

    similares = []
    try:
        hora_nueva = datetime.strptime(hora_llegada, "%H:%M:%S")
    except (ValueError, TypeError):
        return similares

    for id_existente, hora_existente_str, diagnostico_existente, origen_existente in resultados:
        try:
            hora_existente = datetime.strptime(hora_existente_str, "%H:%M:%S")
        except (ValueError, TypeError):
            continue
        diferencia_min = abs((hora_nueva - hora_existente).total_seconds()) / 60
        if diferencia_min <= ventana_minutos:
            similares.append({
                "id": id_existente,
                "hora_llegada": hora_existente_str,
                "diagnostico": diagnostico_existente,
                "origen_pc": origen_existente,
            })
    return similares


def insertar_atencion_con_id(datos, estudiante_id):
    """Inserta una atención preservando su id y demás campos originales (usado al importar)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO atenciones (
            id, estudiante_id, fecha, hora_llegada, hora_salida, saturacion,
            temperatura, frecuencia_cardiaca, diagnostico, recomendacion,
            enfermera_responsable, origen_pc, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos["id"], estudiante_id, datos["fecha"], datos["hora_llegada"], datos.get("hora_salida"),
        datos.get("saturacion"), datos.get("temperatura"), datos.get("frecuencia_cardiaca"),
        datos.get("diagnostico"), datos.get("recomendacion"), datos.get("enfermera_responsable"),
        datos.get("origen_pc"), datos.get("fecha_registro"),
    ))
    conexion.commit()
    conexion.close()

def procesar_importacion(paquete):
    """
    Procesa un paquete de importación (diccionario ya cargado desde JSON).
    Inserta automáticamente estudiantes nuevos y atenciones sin conflicto.
    Devuelve (resumen, atenciones_para_revisar) donde las atenciones con
    posible duplicado NO se insertan; quedan pendientes de decisión manual.
    """
    estudiantes_importados = paquete.get("estudiantes", [])
    atenciones_importadas = paquete.get("atenciones", [])

    mapa_estudiantes = {}  # id_original_del_import -> id a usar en esta BD local
    estudiantes_nuevos = 0
    estudiantes_reutilizados = 0

    for est in estudiantes_importados:
        id_import = est["id"]

        if existe_estudiante_id(id_import):
            mapa_estudiantes[id_import] = id_import
            continue

        id_local_existente = buscar_estudiante_exacto(est["nombre"], est["curso"], est.get("paralelo"))
        if id_local_existente:
            mapa_estudiantes[id_import] = id_local_existente
            estudiantes_reutilizados += 1
            continue

        insertar_estudiante_con_id(
            id_import, est["nombre"], est["curso"], est.get("paralelo"),
            est.get("sexo"), est.get("origen_pc"), est.get("fecha_creacion")
        )
        mapa_estudiantes[id_import] = id_import
        estudiantes_nuevos += 1

    atenciones_nuevas = 0
    atenciones_ya_existentes = 0
    atenciones_para_revisar = []

    for at in atenciones_importadas:
        if existe_atencion_id(at["id"]):
            atenciones_ya_existentes += 1
            continue

        estudiante_id_local = mapa_estudiantes.get(at["estudiante_id"], at["estudiante_id"])
        similares = buscar_atenciones_similares(estudiante_id_local, at["fecha"], at["hora_llegada"])

        if similares:
            atenciones_para_revisar.append({
                "atencion_importada": at,
                "estudiante_id_local": estudiante_id_local,
                "similares_existentes": similares,
            })
            continue

        insertar_atencion_con_id(at, estudiante_id_local)
        atenciones_nuevas += 1

    resumen = {
        "estudiantes_nuevos": estudiantes_nuevos,
        "estudiantes_reutilizados": estudiantes_reutilizados,
        "atenciones_nuevas": atenciones_nuevas,
        "atenciones_ya_existentes": atenciones_ya_existentes,
        "atenciones_para_revisar": len(atenciones_para_revisar),
    }
    return resumen, atenciones_para_revisar

def registrar_log_sincronizacion(registros_nuevos, duplicados_detectados, notas):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO log_sincronizacion (
            id, registros_nuevos_pc1, registros_nuevos_pc2,
            duplicados_detectados, duplicados_resueltos, notas
        ) VALUES (?, ?, 0, ?, 0, ?)
    """, (str(uuid.uuid4()), registros_nuevos, duplicados_detectados, notas))
    conexion.commit()
    conexion.close()

# ==========================================================
# USUARIOS
# ==========================================================

def existe_usuario(usuario):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None


def crear_usuario(nombre_completo, usuario, password_hash, rol="enfermera"):
    conexion = conectar()
    cursor = conexion.cursor()
    id_usuario = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO usuarios (id, nombre_completo, usuario, password_hash, rol, activo)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (id_usuario, nombre_completo, usuario, password_hash, rol))
    conexion.commit()
    conexion.close()
    return id_usuario

def obtener_usuario_por_usuario(usuario):
    """Devuelve (id, nombre_completo, usuario, password_hash, rol, activo) o None."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre_completo, usuario, password_hash, rol, activo
        FROM usuarios WHERE usuario = ?
    """, (usuario,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

# ==========================================================
# MÉTRICAS Y ALERTAS
# ==========================================================

def contar_atenciones_total_mes(mes):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM atenciones WHERE strftime('%Y-%m', fecha) = ?", (mes,))
    total = cursor.fetchone()[0]
    conexion.close()
    return total


def contar_atenciones_total_global():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM atenciones")
    total = cursor.fetchone()[0]
    conexion.close()
    return total


def contar_estudiantes_distintos_mes(mes):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(DISTINCT estudiante_id) FROM atenciones WHERE strftime('%Y-%m', fecha) = ?", (mes,))
    total = cursor.fetchone()[0]
    conexion.close()
    return total


def promedio_atenciones_por_dia_global():
    """Promedio de atenciones por día, considerando solo los días en que sí hubo al menos una."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT fecha) FROM atenciones")
    total, dias = cursor.fetchone()
    conexion.close()
    if not dias:
        return 0
    return round(total / dias, 1)


def listar_estudiantes_frecuentes():
    """
    Estudiantes con 3+ atenciones en la SEMANA actual o 5+ en el MES actual.
    Se calcula sobre la fecha real de hoy (no depende de ningún filtro de la vista).
    """
    hoy = datetime.now()
    semana_actual = hoy.strftime("%Y-%W")
    mes_actual = hoy.strftime("%Y-%m")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.id, e.nombre, e.curso, e.paralelo,
               SUM(CASE WHEN strftime('%Y-%W', a.fecha) = ? THEN 1 ELSE 0 END) AS conteo_semana,
               SUM(CASE WHEN strftime('%Y-%m', a.fecha) = ? THEN 1 ELSE 0 END) AS conteo_mes
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        GROUP BY e.id
        HAVING conteo_semana >= 3 OR conteo_mes >= 5
        ORDER BY conteo_mes DESC, conteo_semana DESC
    """, (semana_actual, mes_actual))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def obtener_frecuencia_estudiante(estudiante_id):
    """Devuelve (conteo_semana_actual, conteo_mes_actual) para UN estudiante específico."""
    hoy = datetime.now()
    semana_actual = hoy.strftime("%Y-%W")
    mes_actual = hoy.strftime("%Y-%m")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN strftime('%Y-%W', fecha) = ? THEN 1 ELSE 0 END),
            SUM(CASE WHEN strftime('%Y-%m', fecha) = ? THEN 1 ELSE 0 END)
        FROM atenciones WHERE estudiante_id = ?
    """, (semana_actual, mes_actual, estudiante_id))
    fila = cursor.fetchone()
    conexion.close()
    return (fila[0] or 0), (fila[1] or 0)


def listar_usuarios_por_ids(ids_usuarios):
    """Devuelve {id: nombre_completo} para un conjunto de ids de usuarios (usado al exportar a Excel)."""
    ids_usuarios = [i for i in ids_usuarios if i]
    if not ids_usuarios:
        return {}
    conexion = conectar()
    cursor = conexion.cursor()
    placeholders = ",".join("?" for _ in ids_usuarios)
    cursor.execute(f"SELECT id, nombre_completo FROM usuarios WHERE id IN ({placeholders})", ids_usuarios)
    resultado = dict(cursor.fetchall())
    conexion.close()
    return resultado