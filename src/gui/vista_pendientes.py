"""
Vista de Atenciones Pendientes: muestra TODAS las atenciones (sin importar
la fecha) que aún no tienen hora de salida registrada. Sirve para que no se
"pierdan" de vista si se olvida marcar la salida el mismo día.
"""

import customtkinter as ctk
from gui import estilos

from database.consultas import (
    listar_atenciones_pendientes,
    cerrar_atencion,
)


class VistaPendientes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._crear_widgets()
        self._cargar_pendientes()

    def _crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="Atenciones con Salida Pendiente", font=estilos.fuente_titulo())
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.label_total = ctk.CTkLabel(self, text="", text_color=estilos.COLOR_TEXTO_GRIS)
        self.label_total.grid(row=1, column=0, sticky="w", pady=(0, 15))

        # --- Encabezados ---
        frame_encabezados = ctk.CTkFrame(self)
        frame_encabezados.grid(row=2, column=0, sticky="new")

        pesos = [1, 1, 2, 1, 1, 1]
        for i, peso in enumerate(pesos):
            frame_encabezados.grid_columnconfigure(i, weight=peso)

        encabezados = ["Fecha", "Hora llegada", "Estudiante", "Curso", "Paralelo", ""]
        for i, texto in enumerate(encabezados):
            ctk.CTkLabel(
                frame_encabezados, text=texto, font=estilos.fuente_etiqueta(), anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # --- Tabla scrollable ---
        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_tabla.grid(row=3, column=0, sticky="nsew")
        self.grid_rowconfigure(3, weight=1)
        for i, peso in enumerate(pesos):
            self.frame_tabla.grid_columnconfigure(i, weight=peso)

    def _cargar_pendientes(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        pendientes = listar_atenciones_pendientes()
        self.label_total.configure(
            text=f"{len(pendientes)} atención(es) sin hora de salida registrada"
        )

        if not pendientes:
            ctk.CTkLabel(
                self.frame_tabla, text="No hay atenciones pendientes. ✅", text_color=estilos.COLOR_TEXTO_GRIS
            ).grid(row=0, column=0, columnspan=6, padx=10, pady=20, sticky="w")
            return

        # pendientes: id, estudiante_id, fecha, hora_llegada, hora_salida, saturacion,
        #             temperatura, frecuencia_cardiaca, diagnostico, recomendacion,
        #             enfermera_responsable, origen_pc, fecha_registro, nombre, curso, paralelo, sexo
        for fila_idx, atencion in enumerate(pendientes):
            id_atencion = atencion[0]
            fecha = atencion[2]
            hora_llegada = atencion[3]
            nombre = atencion[-4]
            curso = atencion[-3]
            paralelo = atencion[-2]

            ctk.CTkLabel(self.frame_tabla, text=fecha, anchor="w").grid(
                row=fila_idx, column=0, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=hora_llegada, anchor="w").grid(
                row=fila_idx, column=1, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=nombre, anchor="w").grid(
                row=fila_idx, column=2, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=curso, anchor="w").grid(
                row=fila_idx, column=3, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=paralelo or "—", anchor="w").grid(
                row=fila_idx, column=4, padx=10, pady=6, sticky="w"
            )

            btn_salida = ctk.CTkButton(
                self.frame_tabla, text="Marcar salida",
                width=estilos.ANCHO_BOTON_ACCION + 10, height=estilos.ALTO_BOTON_ACCION,
                command=lambda i=id_atencion: self._marcar_salida(i)
            )
            btn_salida.grid(row=fila_idx, column=5, padx=10, pady=4, sticky="e")

    def _marcar_salida(self, id_atencion):
        cerrar_atencion(id_atencion)
        self._cargar_pendientes()