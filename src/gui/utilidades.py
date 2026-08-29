"""
Funciones auxiliares reutilizables para los widgets de la interfaz.
"""

def forzar_mayusculas(entry):
    """
    Convierte el contenido de un CTkEntry a mayúsculas mientras el usuario
    escribe, preservando la posición del cursor para que no salte al final
    en cada tecla presionada.
    """
    texto = entry.get()
    texto_mayus = texto.upper()
    if texto != texto_mayus:
        posicion_cursor = entry.index("insert")
        entry.delete(0, "end")
        entry.insert(0, texto_mayus)
        entry.icursor(posicion_cursor)