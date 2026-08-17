"""
Módulo encargado de crear la estructura de la base de datos SQLite
para el Sistema de Enfermería.
"""

import sqlite3
import os

RUTA_BD = os.path.join(os.path.dirname(__file__), "..", "..", "data", "enfermeria.db")


def conectar():
    """Crea y devuelve una conexión a la base de datos SQLite."""
    os.makedirs(os.path.dirname(RUTA_BD), exist_ok=True)
    conexion = sqlite3.connect(RUTA_BD)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_tablas():
    """Crea todas las tablas del sistema si no existen aún."""
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla: estudiantes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            paralelo TEXT NOT NULL,
            origen_pc TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla: usuarios
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

    # Tabla: atenciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atenciones (
            id TEXT PRIMARY KEY,
            estudiante_id TEXT NOT NULL,
            fecha DATE NOT NULL,
            hora_llegada TIME NOT NULL,
            hora_salida TIME,
            saturacion INTEGER,
            temperatura REAL,
            frecuencia_cardiaca INTEGER,
            diagnostico TEXT,
            recomendacion TEXT,
            enfermera_responsable TEXT,
            origen_pc TEXT NOT NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
            FOREIGN KEY (enfermera_responsable) REFERENCES usuarios(id)
        )
    """)

    # Tabla: log_sincronizacion
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