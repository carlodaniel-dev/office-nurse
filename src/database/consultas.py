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

def crear_estudiante(nombre, paralelo):
    """Inserta un nuevo estudiante. Devuelve el id (UUID) generado."""
    id_estudiante = str(uuid.uuid4())
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO estudiantes (id, nombre, paralelo, origen_pc)
        VALUES (?, ?, ?, ?)
    """, (id_estudiante, nombre, paralelo, ORIGEN_PC))

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
        SELECT id, nombre, paralelo FROM estudiantes
        WHERE nombre LIKE ?
        ORDER BY nombre
        LIMIT ?
    """, (patron, limite))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def buscar_estudiante_exacto(nombre, paralelo):
    """Busca coincidencia exacta de nombre + paralelo (para evitar duplicados al crear)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id FROM estudiantes
        WHERE LOWER(nombre) = LOWER(?) AND paralelo = ?
    """, (nombre.strip(), paralelo))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None


def obtener_estudiante_por_id(id_estudiante):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estudiantes WHERE id = ?", (id_estudiante,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado


def listar_estudiantes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estudiantes ORDER BY nombre")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


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
        SELECT a.*, e.nombre, e.paralelo
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE a.fecha = ?
        ORDER BY a.hora_llegada
    """, (fecha,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def listar_atenciones_por_estudiante(estudiante_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT * FROM atenciones
        WHERE estudiante_id = ?
        ORDER BY fecha DESC, hora_llegada DESC
    """, (estudiante_id,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados