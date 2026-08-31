"""
Configuración local de esta instalación del sistema.
Cada PC tiene su propio archivo data/config.json (nunca se comparte
entre PCs ni se sube al repositorio), donde se guarda su identificador
(PC1 o PC2) una sola vez, la primera vez que se ejecuta el programa.
"""

import json
import os

RUTA_CONFIG = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")


def cargar_configuracion():
    if not os.path.exists(RUTA_CONFIG):
        return {}
    try:
        with open(RUTA_CONFIG, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_configuracion(config):
    os.makedirs(os.path.dirname(RUTA_CONFIG), exist_ok=True)
    with open(RUTA_CONFIG, "w", encoding="utf-8") as archivo:
        json.dump(config, archivo, ensure_ascii=False, indent=2)


def obtener_origen_pc():
    """Devuelve el identificador de esta PC (PC1/PC2), o None si aún no está configurado."""
    return cargar_configuracion().get("origen_pc")


def guardar_origen_pc(valor):
    config = cargar_configuracion()
    config["origen_pc"] = valor
    guardar_configuracion(config)