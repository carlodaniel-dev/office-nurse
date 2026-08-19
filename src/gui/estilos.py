"""
Constantes de estilo visual usadas en toda la interfaz.
Centraliza colores, fuentes y tamaños para mantener consistencia
entre las distintas vistas del sistema.
"""

import customtkinter as ctk

# ---------- Colores ----------
COLOR_PELIGRO = "#B3261E"          # acciones destructivas (eliminar)
COLOR_PELIGRO_HOVER = "#8C1D18"

COLOR_TEXTO_GRIS = "gray"
COLOR_SUGERENCIA_FONDO = ("gray90", "gray20")

COLOR_VERDE = "#D8F768"
COLOR_VERDE_HOVER = "#95AA48"

COLOR_AMARILLO = "#FFC72C"
COLOR_AMARILLO_HOVER = "#816517"

COLOR_NEGRO = "#1C1C1C"
COLOR_NEGRO_SUAVE = "#4B4949"

# ---------- Fuentes ----------
def fuente_titulo():
    return ctk.CTkFont(size=22, weight="bold")

def fuente_subtitulo():
    return ctk.CTkFont(size=18, weight="bold")

def fuente_seccion():
    return ctk.CTkFont(size=16, weight="bold")

def fuente_seccion_pequena():
    return ctk.CTkFont(size=14, weight="bold")

def fuente_etiqueta():
    return ctk.CTkFont(weight="bold")

def fuente_valor_destacado():
    return ctk.CTkFont(size=16, weight="bold")

def fuente_pequena():
    return ctk.CTkFont(size=11)

# ---------- Tamaños de botones ----------
ALTO_BOTON_ACCION = 26
ANCHO_BOTON_ACCION = 100
ANCHO_BOTON_ACCION_ANGOSTO = 70