"""
Módulo encargado de crear la estructura de la base de datos SQLite
"""

import sqlite3
import os

# Ruta donde se guardará la base de datos
RUTA_BD = os.path.join(os.path.dirname(__file__), "..", "..", "data", "enfermeria.db")


def conectar():
    """Crea y devuelve una conexión a la base de datos SQLite."""
    os.makedirs(os.path.dirname(RUTA_BD), exist_ok=True)
    conexion = sqlite3.connect(RUTA_BD)
    conexion.execute("PRAGMA foreign_keys = ON")  # habilita llaves foráneas
    return conexion


def crear_tablas():
    """Crea todas las tablas del sistema si no existen aún."""
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id TEXT PRIMARY KEY,
            codigo_estudiante TEXT UNIQUE NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            curso_grado TEXT,
            fecha_nacimiento DATE,
            contacto_emergencia TEXT,
            telefono_emergencia TEXT,
            alergias TEXT,
            condiciones_medicas TEXT,
            origen_pc TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nombre_completo TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'enfermera',
            activo BOOLEAN NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atenciones (
            id TEXT PRIMARY KEY,
            estudiante_id TEXT NOT NULL,
            fecha DATE NOT NULL,
            hora_llegada TIME NOT NULL,
            hora_salida TIME,
            motivo_consulta TEXT NOT NULL,
            sintomas TEXT,
            signos_vitales_temp REAL,
            signos_vitales_presion TEXT,
            procedimiento_realizado TEXT,
            medicamento_administrado TEXT,
            observaciones TEXT,
            requiere_seguimiento BOOLEAN DEFAULT 0,
            se_notifico_representante BOOLEAN DEFAULT 0,
            enfermera_responsable TEXT,
            origen_pc TEXT NOT NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
            FOREIGN KEY (enfermera_responsable) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_sincronizacion (
            id TEXT PRIMARY KEY,
            fecha_sincronizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_responsable TEXT,
            registros_nuevos_pc1 INTEGER DEFAULT 0,
            registros_nuevos_pc2 INTEGER DEFAULT 0,
            duplicados_detectados INTEGER DEFAULT 0,
            duplicados_resueltos INTEGER DEFAULT 0,
            notas TEXT
        )
    """)

    conexion.commit()
    conexion.close()
    print("✅ Base de datos y tablas creadas correctamente.")


if __name__ == "__main__":
    crear_tablas()