"""
Ventana principal del Sistema de Enfermería Escolar.
Contiene el menú de navegación y el contenedor donde se muestran las vistas.
"""

import customtkinter as ctk
import os
import time
from PIL import Image
from tkinter import messagebox
from auth import obtener_usuario_actual, cerrar_sesion, cargar_sesion_valida, refrescar_sesion

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

        self.solicito_cerrar_sesion = False

        self._configurar_icono()
        self._crear_menu_lateral()
        self._crear_contenedor_principal()
        self._crear_vistas()

        self.mostrar_vista_atenciones()

        self._ultima_actividad = time.time()
        self._registrar_eventos_actividad()
        self._verificar_sesion_periodicamente()

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
        self.menu_lateral.grid_columnconfigure(0, weight=1)
        self.menu_lateral.grid_rowconfigure(6, weight=1)  # empuja logo + pie hacia abajo

        # --- Fila 0: título ---
        titulo = ctk.CTkLabel(
            self.menu_lateral,
            text="Departamento\nEnfermería",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="left"
        )
        titulo.grid(row=0, column=0, padx=20, pady=(25, 30), sticky="w")

        # --- Filas 1-5: menú de páginas ---
        botones = [
            ("NUEVA ATENCION", self.mostrar_vista_atenciones),
            ("SALIDAS PENDIENTES", self.mostrar_vista_pendientes),
            ("HISTORIAL DE ATENCIONES", self.mostrar_vista_estudiantes),
            ("REPORTES", self.mostrar_vista_reportes),
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

        # --- Fila 6: espaciador flexible (weight=1) empuja lo siguiente al fondo ---

        # --- Fila 7: logo institucional ---
        ruta_logo = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "logo_ammi.png"
        )
        if os.path.exists(ruta_logo):
            imagen_logo = ctk.CTkImage(
                light_image=Image.open(ruta_logo),
                dark_image=Image.open(ruta_logo),
                size=(160, 55)
            )
            label_logo = ctk.CTkLabel(self.menu_lateral, image=imagen_logo, text="")
            label_logo.grid(row=7, column=0, pady=(0, 15), sticky="s")

        # --- Fila 8: nombre de usuario + botón cerrar sesión, en la misma fila ---
        usuario = obtener_usuario_actual()
        nombre_mostrado = usuario["nombre_completo"] if usuario else "Usuario"

        frame_pie = ctk.CTkFrame(self.menu_lateral, fg_color="transparent")
        frame_pie.grid(row=8, column=0, padx=15, pady=(0, 15), sticky="ew")
        frame_pie.grid_columnconfigure(0, weight=1)

        label_usuario = ctk.CTkLabel(
            frame_pie, text=f"👤 {nombre_mostrado}",
            text_color="gray", anchor="w", font=ctk.CTkFont(size=11)
        )
        label_usuario.grid(row=0, column=0, sticky="w")

        btn_cerrar_sesion = ctk.CTkButton(
            frame_pie, text="Salir", width=50, height=24,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            command=self._cerrar_sesion
        )
        btn_cerrar_sesion.grid(row=0, column=1, sticky="e")

    def _crear_contenedor_principal(self):
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

    def _crear_vistas(self):
        """
        Crea las 5 vistas UNA SOLA VEZ y las apila en la misma celda del grid.
        Nunca se destruyen mientras la app está abierta (evita el bug de
        CustomTkinter con el ScalingTracker de los CTkComboBox al cambiar
        de pantalla/DPI).
        """
        from gui.vista_atenciones import VistaAtenciones
        from gui.vista_pendientes import VistaPendientes
        from gui.vista_estudiantes import VistaEstudiantes
        from gui.vista_reportes import VistaReportes
        from gui.vista_sincronizacion import VistaSincronizacion

        self.vista_atenciones = VistaAtenciones(self.contenedor)
        self.vista_pendientes = VistaPendientes(self.contenedor)
        self.vista_estudiantes = VistaEstudiantes(self.contenedor)
        self.vista_reportes = VistaReportes(self.contenedor)
        self.vista_sincronizacion = VistaSincronizacion(self.contenedor)

        for vista in (self.vista_atenciones, self.vista_pendientes, self.vista_estudiantes, self.vista_reportes, self.vista_sincronizacion):
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

    def mostrar_vista_reportes(self):
        self.vista_reportes.tkraise()
        if hasattr(self.vista_reportes, "_cargar_datos"):
            self.vista_reportes._cargar_datos()

    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas cerrar sesión?")
        if not confirmar:
            return
        cerrar_sesion()
        self.solicito_cerrar_sesion = True
        self.destroy()

    def _verificar_sesion_periodicamente(self):
        """
        Revisa cada 30 segundos si ha habido actividad reciente del usuario.
        Si pasaron los minutos configurados SIN ninguna interacción (mouse/
        teclado/clics), cierra la sesión automáticamente. Si hubo actividad,
        refresca la sesión guardada en disco para extender su vigencia.
        """
        from auth import DURACION_SESION_MINUTOS

        segundos_inactivo = time.time() - self._ultima_actividad
        limite_segundos = DURACION_SESION_MINUTOS * 60

        if segundos_inactivo >= limite_segundos:
            messagebox.showwarning(
                "Sesión expirada",
                f"Tu sesión se cerró por {DURACION_SESION_MINUTOS} minutos de inactividad.\n"
                "Debes iniciar sesión de nuevo."
            )
            cerrar_sesion()
            self.solicito_cerrar_sesion = True
            self.destroy()
            return

        refrescar_sesion()
        self.after(30_000, self._verificar_sesion_periodicamente)

    def _registrar_eventos_actividad(self):
        """
        Escucha movimiento de mouse, teclado y clics en TODA la ventana
        (incluyendo ventanas emergentes como editar/detalle), para saber
        cuándo hubo actividad real del usuario.
        """
        for evento in ("<Motion>", "<Key>", "<Button>"):
            self.bind_all(evento, self._marcar_actividad)

    def _marcar_actividad(self, event=None):
        self._ultima_actividad = time.time()


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()