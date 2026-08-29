"""
Punto de entrada del Sistema de Enfermería Escolar.
"""

import sys
import os
import ctypes

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

sys.path.append(os.path.dirname(__file__))

from database.modelos import crear_tablas
from auth import cargar_sesion_valida, establecer_usuario_actual
from gui.vista_principal import VentanaPrincipal


def main():
    crear_tablas()

    while True:
        sesion = cargar_sesion_valida()

        if not sesion:
            from gui.vista_login import VentanaLogin
            login = VentanaLogin()
            login.mainloop()
            if not login.sesion_iniciada:
                return  # el usuario cerró la ventana de login sin iniciar sesión
            sesion = cargar_sesion_valida()

        establecer_usuario_actual(sesion["usuario_id"], sesion["nombre_completo"])

        app = VentanaPrincipal()
        app.mainloop()

        if not getattr(app, "solicito_cerrar_sesion", False):
            break  # se cerró la ventana normalmente, termina el programa


if __name__ == "__main__":
    main()