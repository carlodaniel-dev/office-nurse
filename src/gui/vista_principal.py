import customtkinter as ctk

ctk.set_appearance_mode("light")       # "light", "dark" o "system"
ctk.set_default_color_theme("blue")    # tema de color base


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Enfermería Escolar")
        self.geometry("1100x650")
        self.minsize(900, 550)

        # Configurar grid principal: columna 0 = menú, columna 1 = contenido
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_menu_lateral()
        self._crear_contenedor_principal()

        # Vista inicial al abrir la app
        self.mostrar_vista_atenciones()

    def _crear_menu_lateral(self):
        """Crea el panel lateral con los botones de navegación."""
        self.menu_lateral = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.menu_lateral.grid(row=0, column=0, sticky="nsew")
        self.menu_lateral.grid_rowconfigure(6, weight=1)  # empuja el resto hacia abajo

        titulo = ctk.CTkLabel(
            self.menu_lateral,
            text="🩺 Enfermería\nEscolar",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="left"
        )
        titulo.grid(row=0, column=0, padx=20, pady=(25, 30), sticky="w")

        botones = [
            ("📋  Registrar atención", self.mostrar_vista_atenciones),
            ("🧑‍🎓  Estudiantes", self.mostrar_vista_estudiantes),
            ("🔄  Sincronización", self.mostrar_vista_sincronizacion),
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
        """Frame donde se van a 'inyectar' las distintas vistas."""
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

    def _limpiar_contenedor(self):
        """Elimina la vista actual antes de mostrar una nueva."""
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------
    # Navegación entre vistas
    # ------------------------------------------------------------
    def mostrar_vista_atenciones(self):
        from gui.vista_atenciones import VistaAtenciones
        self._limpiar_contenedor()
        VistaAtenciones(self.contenedor).grid(row=0, column=0, sticky="nsew")

    def mostrar_vista_estudiantes(self):
        from gui.vista_estudiantes import VistaEstudiantes
        self._limpiar_contenedor()
        VistaEstudiantes(self.contenedor).grid(row=0, column=0, sticky="nsew")

    def mostrar_vista_sincronizacion(self):
        from gui.vista_sincronizacion import VistaSincronizacion
        self._limpiar_contenedor()
        VistaSincronizacion(self.contenedor).grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()