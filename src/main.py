"""
Punto de entrada del Sistema de Enfermería Escolar.
"""

import sys
import os
import ctypes

# Declara la app como DPI-aware ANTES de crear cualquier ventana.
# Esto evita que Windows reescale la ventana (incluyendo la barra de
# título) como si fuera una imagen, lo cual la hace ver más pequeña
# o borrosa comparada con otras ventanas nativas.
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-Monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Fallback para Windows más viejos
        except Exception:
            pass

# Permite importar módulos desde src/ sin problemas de rutas
sys.path.append(os.path.dirname(__file__))

from database.modelos import crear_tablas
from gui.vista_principal import VentanaPrincipal


def main():
    crear_tablas()  # se asegura de que la BD y tablas existan al iniciar
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()