"""
Autenticación y manejo de sesión local.
- Hashing de contraseñas con PBKDF2 (usa solo la librería estándar de Python,
  sin dependencias externas que puedan dar problemas de instalación).
- Sesión persistida en data/session.json con expiración de 8 horas, para no
  pedir login cada vez que se abre el programa dentro de la misma jornada.
"""

import hashlib
import os
import json
import secrets
from datetime import datetime, timedelta


RUTA_ULTIMO_USUARIO = os.path.join(os.path.dirname(__file__), "..", "data", "ultimo_usuario.json")
DURACION_SESION_MINUTOS = 2
CODIGO_AUTORIZACION_CUENTAS = "AmmI.2026."

_usuario_actual = None  # se llena en memoria al iniciar sesión, para uso rápido en toda la app


def hash_password(password, salt=None):
    """Genera un hash seguro de la contraseña. Si no se da salt, genera uno nuevo (al crear cuenta)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${hash_bytes.hex()}"


def verificar_password(password, password_hash_guardado):
    """Compara una contraseña ingresada contra el hash guardado en la BD."""
    try:
        salt, _ = password_hash_guardado.split("$")
    except (ValueError, AttributeError):
        return False
    return hash_password(password, salt) == password_hash_guardado


def guardar_sesion(usuario_id, nombre_completo):
    os.makedirs(os.path.dirname(RUTA_ULTIMO_USUARIO), exist_ok=True)
    expira = (datetime.now() + timedelta(minutes=DURACION_SESION_MINUTOS)).strftime("%Y-%m-%d %H:%M:%S")
    with open(RUTA_ULTIMO_USUARIO, "w", encoding="utf-8") as archivo:
        json.dump({
            "usuario_id": usuario_id,
            "nombre_completo": nombre_completo,
            "expira": expira,
        }, archivo)


def cargar_sesion_valida():
    """Devuelve los datos de sesión si existe y no ha expirado; None en cualquier otro caso."""
    if not os.path.exists(RUTA_ULTIMO_USUARIO):
        return None
    try:
        with open(RUTA_ULTIMO_USUARIO, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        expira = datetime.strptime(datos["expira"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expira:
            return None
        return datos
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return None


def cerrar_sesion():
    if os.path.exists(RUTA_ULTIMO_USUARIO):
        os.remove(RUTA_ULTIMO_USUARIO)
    global _usuario_actual
    _usuario_actual = None


def establecer_usuario_actual(usuario_id, nombre_completo):
    global _usuario_actual
    _usuario_actual = {"id": usuario_id, "nombre_completo": nombre_completo}


def obtener_usuario_actual():
    """Devuelve {'id':..., 'nombre_completo':...} del usuario logueado, o None."""
    return _usuario_actual

def guardar_ultimo_usuario(usuario):
    os.makedirs(os.path.dirname(RUTA_ULTIMO_USUARIO), exist_ok=True)
    with open(RUTA_ULTIMO_USUARIO, "w", encoding="utf-8") as archivo:
        json.dump({"usuario": usuario}, archivo)


def cargar_ultimo_usuario():
    if not os.path.exists(RUTA_ULTIMO_USUARIO):
        return ""
    try:
        with open(RUTA_ULTIMO_USUARIO, "r", encoding="utf-8") as archivo:
            return json.load(archivo).get("usuario", "")
    except (json.JSONDecodeError, OSError):
        return ""

def refrescar_sesion():
    """
    Extiende la expiración de la sesión activa, usando el usuario actualmente
    logueado en memoria. Se llama cada vez que se detecta actividad del usuario
    (mouse, teclado, clics) para implementar expiración por INACTIVIDAD,
    no por tiempo fijo desde el login.
    """
    usuario = obtener_usuario_actual()
    if usuario is None:
        return
    guardar_sesion(usuario["id"], usuario["nombre_completo"])