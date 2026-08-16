import uuid
from datetime import datetime
from database.modelos import conectar

# Identifica desde qué PC se está ejecutando el sistema.
# Esto lo usaremos para el campo origen_pc en cada registro.
ORIGEN_PC = "PC1"  # <-- cambiar a "PC2" en la otra computadora

# ==========================================================
# ESTUDIANTES
# ==========================================================

def crear_estudiante(codigo_estudiante, nombres, apellidos, curso_grado=None,
                      fecha_nacimiento=None, contacto_emergencia=None,
                      telefono_emergencia=None, alergias=None,
                      condiciones_medicas=None):
    """Inserta un nuevo estudiante. Devuelve el id (UUID) generado."""
    id_estudiante = str(uuid.uuid4())
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO estudiantes (
            id, codigo_estudiante, nombres, apellidos, curso_grado,
            fecha_nacimiento, contacto_emergencia, telefono_emergencia,
            alergias, condiciones_medicas, origen_pc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_estudiante, codigo_estudiante, nombres, apellidos, curso_grado,
        fecha_nacimiento, contacto_emergencia, telefono_emergencia,
        alergias, condiciones_medicas, ORIGEN_PC
    ))

    conexion.commit()
    conexion.close()
    return id_estudiante


def buscar_estudiante_por_codigo(codigo_estudiante):
    """Busca un estudiante por su código institucional. Devuelve una fila o None."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estudiantes WHERE codigo_estudiante = ?", (codigo_estudiante,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado


def buscar_estudiantes_por_nombre(texto_busqueda):
    """Busca estudiantes cuyo nombre o apellido contenga el texto dado."""
    conexion = conectar()
    cursor = conexion.cursor()
    patron = f"%{texto_busqueda}%"
    cursor.execute("""
        SELECT * FROM estudiantes
        WHERE nombres LIKE ? OR apellidos LIKE ?
        ORDER BY apellidos, nombres
    """, (patron, patron))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def listar_estudiantes():
    """Devuelve todos los estudiantes registrados."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estudiantes ORDER BY apellidos, nombres")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def actualizar_estudiante(id_estudiante, **campos):
    """
    Actualiza campos específicos de un estudiante.
    Uso: actualizar_estudiante(id, alergias="Penicilina", curso_grado="9no B")
    """
    if not campos:
        return False

    columnas = ", ".join(f"{campo} = ?" for campo in campos.keys())
    valores = list(campos.values()) + [id_estudiante]

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(f"UPDATE estudiantes SET {columnas} WHERE id = ?", valores)
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    return filas_afectadas > 0


# ==========================================================
# ATENCIONES
# ==========================================================

def crear_atencion(estudiante_id, motivo_consulta, hora_llegada=None, fecha=None,
                    sintomas=None, signos_vitales_temp=None, signos_vitales_presion=None,
                    procedimiento_realizado=None, medicamento_administrado=None,
                    observaciones=None, requiere_seguimiento=False,
                    se_notifico_representante=False, enfermera_responsable=None):
    """Registra una nueva atención de enfermería. Devuelve el id (UUID) generado."""
    id_atencion = str(uuid.uuid4())
    fecha = fecha or datetime.now().strftime("%Y-%m-%d")
    hora_llegada = hora_llegada or datetime.now().strftime("%H:%M:%S")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO atenciones (
            id, estudiante_id, fecha, hora_llegada, motivo_consulta,
            sintomas, signos_vitales_temp, signos_vitales_presion,
            procedimiento_realizado, medicamento_administrado, observaciones,
            requiere_seguimiento, se_notifico_representante,
            enfermera_responsable, origen_pc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_atencion, estudiante_id, fecha, hora_llegada, motivo_consulta,
        sintomas, signos_vitales_temp, signos_vitales_presion,
        procedimiento_realizado, medicamento_administrado, observaciones,
        requiere_seguimiento, se_notifico_representante,
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
        SELECT a.*, e.nombres, e.apellidos, e.curso_grado
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE a.fecha = ?
        ORDER BY a.hora_llegada
    """, (fecha,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def listar_atenciones_por_estudiante(estudiante_id):
    """Devuelve el historial completo de atenciones de un estudiante."""
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


def listar_atenciones_pendientes_seguimiento():
    """Devuelve atenciones marcadas como que requieren seguimiento."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.*, e.nombres, e.apellidos
        FROM atenciones a
        JOIN estudiantes e ON a.estudiante_id = e.id
        WHERE a.requiere_seguimiento = 1
        ORDER BY a.fecha DESC
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados