"""
Ventana principal del Sistema de Enfermería Escolar.
Contiene el menú de navegación y el contenedor donde se muestran las vistas.
"""

import customtkinter as ctk
import os
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(
    os.path.join(os.path.dirname(__file__), "tema_escuela.json")
)


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Registro de Atenciones - Enfermería | AMMI")
        self.geometry("1100x700")
        self.minsize(900, 550)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._configurar_icono()
        self._crear_menu_lateral()
        self._crear_contenedor_principal()
        self._crear_vistas()

        self.mostrar_vista_atenciones()

    def _configurar_icono(self):
        """
        Configura el ícono de la ventana (barra de título y barra de tareas).
        Se aplica con un pequeño retraso (self.after) porque CustomTkinter a veces
        sobreescribe el ícono con el predeterminado de Tkinter justo después de crear
        la ventana; el retraso evita que eso pase.
        """
        ruta_icono = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "escudo_ammi.ico"
        )
        if os.path.exists(ruta_icono):
            self.after(250, lambda: self.iconbitmap(ruta_icono))

    def _crear_menu_lateral(self):
        self.menu_lateral = ctk.CTkFrame(self, width=170, corner_radius=0)
        self.menu_lateral.grid(row=0, column=0, sticky="nsew")
        self.menu_lateral.grid_rowconfigure(6, weight=1)

        titulo = ctk.CTkLabel(
            self.menu_lateral,
            text="Departamento\nEnfermería",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="left"
        )
        titulo.grid(row=0, column=0, padx=20, pady=(25, 30), sticky="w")

        botones = [
            ("NUEVA ATENCION", self.mostrar_vista_atenciones),
            ("ATENCIONES PENDIENTES", self.mostrar_vista_pendientes),
            ("ESTUDIANTES", self.mostrar_vista_estudiantes),
            ("SINCRONIZACION", self.mostrar_vista_sincronizacion),
        ]

        for i, (texto, comando) in enumerate(botones, start=1):
            boton = ctk.CTkButton(
                self.menu_lateral,
                text=texto,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=comando
            )
            boton.grid(row=i, column=0, padx=15, pady=6, sticky="ew")

        # --- Logo institucional (parte inferior del menú) ---
        ruta_logo = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "logo_ammi.png"
        )
        if os.path.exists(ruta_logo):
            imagen_logo = ctk.CTkImage(
                light_image=Image.open(ruta_logo),
                dark_image=Image.open(ruta_logo),
                size=(160, 75)
            )
            label_logo = ctk.CTkLabel(self.menu_lateral, image=imagen_logo, text="")
            label_logo.grid(row=7, column=0, pady=(0, 15), sticky="s")

    def _crear_contenedor_principal(self):
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

    def _crear_vistas(self):
        """
        Crea las 4 vistas UNA SOLA VEZ y las apila en la misma celda del grid.
        Nunca se destruyen mientras la app está abierta (evita el bug de
        CustomTkinter con el ScalingTracker de los CTkComboBox al cambiar
        de pantalla/DPI).
        """
        from gui.vista_atenciones import VistaAtenciones
        from gui.vista_pendientes import VistaPendientes
        from gui.vista_estudiantes import VistaEstudiantes
        from gui.vista_sincronizacion import VistaSincronizacion

        self.vista_atenciones = VistaAtenciones(self.contenedor)
        self.vista_pendientes = VistaPendientes(self.contenedor)
        self.vista_estudiantes = VistaEstudiantes(self.contenedor)
        self.vista_sincronizacion = VistaSincronizacion(self.contenedor)

        for vista in (self.vista_atenciones, self.vista_pendientes, self.vista_estudiantes, self.vista_sincronizacion):
            vista.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------
    # Navegación entre vistas (solo trae al frente la que corresponde)
    # ------------------------------------------------------------
    def mostrar_vista_atenciones(self):
        self.vista_atenciones.tkraise()
        if hasattr(self.vista_atenciones, "_cargar_atenciones_del_dia"):
            self.vista_atenciones._cargar_atenciones_del_dia()

    def mostrar_vista_pendientes(self):
        self.vista_pendientes.tkraise()
        if hasattr(self.vista_pendientes, "_cargar_pendientes"):
            self.vista_pendientes._cargar_pendientes()

    def mostrar_vista_estudiantes(self):
        self.vista_estudiantes.tkraise()
        if hasattr(self.vista_estudiantes, "_cargar_atenciones"):
            self.vista_estudiantes._cargar_atenciones()

    def mostrar_vista_sincronizacion(self):
        self.vista_sincronizacion.tkraise()


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()