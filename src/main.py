"""
Punto de entrada del Sistema de Enfermería Escolar.
"""

import sys
import os

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