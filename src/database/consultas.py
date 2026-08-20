"""
Módulo de consultas (CRUD) para estudiantes y atenciones.
"""

import uuid
from datetime import datetime
from database.modelos import conectar

ORIGEN_PC = "PC1"  # <-- cambiar a "PC2" en la otra computadora

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
    """, (id_estudiante, nombre, curso, paralelo, sexo, ORIGEN_PC))

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
        enfermera_responsable, ORIGEN_PC
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