"""
Ventana principal del Sistema de Enfermería Escolar.
Contiene el menú de navegación y el contenedor donde se muestran las vistas.
"""

import customtkinter as ctk
import os

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

        self._crear_menu_lateral()
        self._crear_contenedor_principal()
        self._crear_vistas()

        self.mostrar_vista_atenciones()

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
            ("REGISTRAR ATENCION", self.mostrar_vista_atenciones),
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

    def _crear_contenedor_principal(self):
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

    def _crear_vistas(self):
        """
        Crea las 3 vistas UNA SOLA VEZ y las apila en la misma celda del grid.
        Nunca se destruyen mientras la app está abierta (evita el bug de
        CustomTkinter con el ScalingTracker de los CTkComboBox al cambiar
        de pantalla/DPI).
        """
        from gui.vista_atenciones import VistaAtenciones
        from gui.vista_estudiantes import VistaEstudiantes
        from gui.vista_sincronizacion import VistaSincronizacion

        self.vista_atenciones = VistaAtenciones(self.contenedor)
        self.vista_estudiantes = VistaEstudiantes(self.contenedor)
        self.vista_sincronizacion = VistaSincronizacion(self.contenedor)

        for vista in (self.vista_atenciones, self.vista_estudiantes, self.vista_sincronizacion):
            vista.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------
    # Navegación entre vistas (solo trae al frente la que corresponde)
    # ------------------------------------------------------------
    def mostrar_vista_atenciones(self):
        self.vista_atenciones.tkraise()
        if hasattr(self.vista_atenciones, "_cargar_atenciones_del_dia"):
            self.vista_atenciones._cargar_atenciones_del_dia()

    def mostrar_vista_estudiantes(self):
        self.vista_estudiantes.tkraise()
        if hasattr(self.vista_estudiantes, "_cargar_estudiantes"):
            self.vista_estudiantes._cargar_estudiantes()

    def mostrar_vista_sincronizacion(self):
        self.vista_sincronizacion.tkraise()


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()