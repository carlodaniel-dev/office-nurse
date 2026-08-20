"""
Vista de Historial de Atenciones: muestra cada visita a enfermería registrada,
con datos del estudiante (nombre, curso, paralelo) y de la atención (fecha, diagnóstico).
Permite editar o eliminar cada registro.
"""

import customtkinter as ctk
from tkinter import messagebox
from gui import estilos
from gui.constantes import CURSOS, PARALELOS, DIAGNOSTICOS

from database.consultas import (
    listar_todas_atenciones,
    filtrar_atenciones,
    actualizar_estudiante,
    actualizar_atencion,
    eliminar_atencion,
)


class VistaEstudiantes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._crear_widgets()
        self._cargar_atenciones()

    def _crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="Historial de atenciones", font=estilos.fuente_titulo())
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Buscador ---
        frame_buscador = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscador.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        frame_buscador.grid_columnconfigure(0, weight=1)

        self.entry_buscar = ctk.CTkEntry(
            frame_buscador, placeholder_text="Buscar por nombre, curso, paralelo o diagnóstico..."
        )
        self.entry_buscar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_atenciones())

        self.label_total = ctk.CTkLabel(frame_buscador, text="", text_color=estilos.COLOR_TEXTO_GRIS)
        self.label_total.grid(row=0, column=1, sticky="e")

        # --- Encabezados de la tabla ---
        frame_encabezados = ctk.CTkFrame(self)
        frame_encabezados.grid(row=2, column=0, sticky="new")

        pesos = [2, 1, 2, 1, 1, 1]
        for i, peso in enumerate(pesos):
            frame_encabezados.grid_columnconfigure(i, weight=peso)

        encabezados = ["Nombre", "Fecha", "Diagnóstico", "Curso", "Paralelo", "", ""]
        for i, texto in enumerate(encabezados):
            ctk.CTkLabel(
                frame_encabezados, text=texto, font=estilos.fuente_etiqueta(), anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # --- Tabla scrollable ---
        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_tabla.grid(row=3, column=0, sticky="nsew")
        for i, peso in enumerate(pesos):
            self.frame_tabla.grid_columnconfigure(i, weight=peso)

    def _cargar_atenciones(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        texto = self.entry_buscar.get().strip()
        atenciones = filtrar_atenciones(texto) if texto else listar_todas_atenciones()

        self.label_total.configure(text=f"{len(atenciones)} atención(es)")

        if not atenciones:
            ctk.CTkLabel(self.frame_tabla, text="No se encontraron atenciones.", text_color=estilos.COLOR_TEXTO_GRIS).grid(
                row=0, column=0, columnspan=6, padx=10, pady=20, sticky="w"
            )
            return

        # atenciones: id, estudiante_id, fecha, hora_llegada, hora_salida, saturacion,
        #             temperatura, frecuencia_cardiaca, diagnostico, recomendacion,
        #             enfermera_responsable, origen_pc, fecha_registro, nombre, curso, paralelo, sexo
        for fila_idx, atencion in enumerate(atenciones):
            fecha = atencion[2]
            diagnostico = atencion[8]
            nombre = atencion[-4]
            curso = atencion[-3]
            paralelo = atencion[-2]

            ctk.CTkLabel(self.frame_tabla, text=nombre, anchor="w").grid(
                row=fila_idx, column=0, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=fecha, anchor="w").grid(
                row=fila_idx, column=1, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=diagnostico or "—", anchor="w").grid(
                row=fila_idx, column=2, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=curso, anchor="w").grid(
                row=fila_idx, column=3, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=paralelo or "—", anchor="w").grid(
                row=fila_idx, column=4, padx=10, pady=6, sticky="w"
            )

            frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
            frame_acciones.grid(row=fila_idx, column=5, padx=10, pady=4, sticky="e")

            btn_editar = ctk.CTkButton(
                frame_acciones, text="✏️", width=32, height=28,
                fg_color=estilos.COLOR_AMARILLO, hover_color=estilos.COLOR_AMARILLO_HOVER,
                command=lambda a=atencion: self._abrir_editor_atencion(a)
            )
            btn_editar.pack(side="left", padx=(0, 6))

            btn_eliminar = ctk.CTkButton(
                frame_acciones, text="🗑️", width=32, height=28,
                fg_color=estilos.COLOR_PELIGRO, hover_color=estilos.COLOR_PELIGRO_HOVER,
                command=lambda i=atencion[0], n=nombre, f=fecha: self._confirmar_eliminar(i, n, f)
            )
            btn_eliminar.pack(side="left")

    # ------------------------------------------------------------
    # Editar atención (datos del estudiante + datos clínicos de esa visita)
    # ------------------------------------------------------------
    def _abrir_editor_atencion(self, atencion):
        id_atencion = atencion[0]
        estudiante_id = atencion[1]
        hora_llegada = atencion[3]
        hora_salida = atencion[4]
        saturacion = atencion[5]
        temperatura = atencion[6]
        frecuencia = atencion[7]
        diagnostico = atencion[8]
        recomendacion = atencion[9]
        nombre = atencion[-4]
        curso = atencion[-3]
        paralelo = atencion[-2]
        sexo = atencion[-1]

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar atención")
        ventana.geometry("460x735")
        ventana.grab_set()

        contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)

        # --- Datos del estudiante ---
        ctk.CTkLabel(contenedor, text="Datos del estudiante", font=estilos.fuente_seccion_pequena(), anchor="w").grid(
            row=0, column=0, columnspan=2, pady=(0, 8), sticky="w"
        )

        ctk.CTkLabel(contenedor, text="Nombre", anchor="w").grid(row=1, column=0, columnspan=2, sticky="w")
        entry_nombre = ctk.CTkEntry(contenedor)
        entry_nombre.insert(0, nombre)
        entry_nombre.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Curso", anchor="w").grid(row=3, column=0, padx=(0, 5), sticky="w")
        combo_curso = ctk.CTkComboBox(contenedor, values=CURSOS, state="readonly")
        combo_curso.set(curso)
        combo_curso.grid(row=4, column=0, padx=(0, 5), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Paralelo", anchor="w").grid(row=3, column=1, padx=(5, 0), sticky="w")
        combo_paralelo = ctk.CTkComboBox(contenedor, values=PARALELOS, state="readonly")
        combo_paralelo.set(paralelo or "")
        combo_paralelo.grid(row=4, column=1, padx=(5, 0), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Sexo", anchor="w").grid(row=5, column=0, columnspan=2, sticky="w")
        var_sexo = ctk.StringVar(value=sexo or "")
        ctk.CTkSegmentedButton(contenedor, values=["Masculino", "Femenino"], variable=var_sexo).grid(
            row=6, column=0, columnspan=2, pady=(0, 15), sticky="ew"
        )

        # --- Datos clínicos de la visita ---
                # --- Horas (solo lectura, no editables) ---
        ctk.CTkLabel(contenedor, text="Datos de la atención", font=estilos.fuente_seccion_pequena(), anchor="w").grid(
            row=7, column=0, columnspan=2, pady=(0, 8), sticky="w"
        )

        frame_horas = ctk.CTkFrame(contenedor)
        frame_horas.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        frame_horas.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            frame_horas, text=f"Llegada: {hora_llegada}",
            text_color=estilos.COLOR_TEXTO_GRIS, anchor="w"
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(
            frame_horas, text=f"Salida: {hora_salida or 'Pendiente'}",
            text_color=estilos.COLOR_TEXTO_GRIS, anchor="e"
        ).grid(row=0, column=1, padx=15, pady=10, sticky="e")
        
        
        ctk.CTkLabel(contenedor, text="Datos de la atención", font=estilos.fuente_seccion_pequena(), anchor="w").grid(
            row=7, column=0, columnspan=2, pady=(0, 8), sticky="w"
        )

        ctk.CTkLabel(contenedor, text="Saturación (%)", anchor="w").grid(row=9, column=0, padx=(0, 5), sticky="w")
        entry_saturacion = ctk.CTkEntry(contenedor)
        entry_saturacion.insert(0, "" if saturacion is None else str(saturacion))
        entry_saturacion.grid(row=10, column=0, padx=(0, 5), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Frecuencia cardíaca (lpm)", anchor="w").grid(row=9, column=1, padx=(5, 0), sticky="w")
        entry_frecuencia = ctk.CTkEntry(contenedor)
        entry_frecuencia.insert(0, "" if frecuencia is None else str(frecuencia))
        entry_frecuencia.grid(row=10, column=1, padx=(5, 0), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Temperatura (°C)", anchor="w").grid(row=11, column=0, columnspan=2, sticky="w")
        entry_temperatura = ctk.CTkEntry(contenedor)
        entry_temperatura.insert(0, "" if temperatura is None else str(temperatura))
        entry_temperatura.grid(row=12, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Diagnóstico", anchor="w").grid(row=13, column=0, columnspan=2, sticky="w")
        combo_diagnostico = ctk.CTkComboBox(contenedor, values=DIAGNOSTICOS, state="readonly")
        combo_diagnostico.set(diagnostico if diagnostico in DIAGNOSTICOS else "Otros")
        combo_diagnostico.grid(row=14, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        entry_diagnostico_otro = ctk.CTkEntry(contenedor, placeholder_text="Especifique el diagnóstico")
        if diagnostico not in DIAGNOSTICOS:
            entry_diagnostico_otro.insert(0, diagnostico or "")

        def on_cambiar_diagnostico(valor):
            if valor == "Otros":
                entry_diagnostico_otro.grid(row=15, column=0, columnspan=2, pady=(0, 10), sticky="ew")
            else:
                entry_diagnostico_otro.grid_forget()

        combo_diagnostico.configure(command=on_cambiar_diagnostico)
        if diagnostico not in DIAGNOSTICOS:
            entry_diagnostico_otro.grid(row=15, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(contenedor, text="Recomendación", anchor="w").grid(row=16, column=0, columnspan=2, sticky="w")
        textbox_recomendacion = ctk.CTkTextbox(contenedor, height=60)
        textbox_recomendacion.insert("1.0", recomendacion or "")
        textbox_recomendacion.grid(row=17, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        def guardar():
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_curso = combo_curso.get().strip()
            nuevo_paralelo = combo_paralelo.get().strip()
            nuevo_sexo = var_sexo.get().strip()

            if not nuevo_nombre or not nuevo_curso or not nuevo_paralelo or not nuevo_sexo:
                messagebox.showwarning("Atención", "Los datos del estudiante son obligatorios.", parent=ventana)
                return

            diagnostico_sel = combo_diagnostico.get().strip()
            if diagnostico_sel == "Otros":
                nuevo_diagnostico = entry_diagnostico_otro.get().strip()
                if not nuevo_diagnostico:
                    messagebox.showwarning("Atención", "Especifica el diagnóstico.", parent=ventana)
                    return
            else:
                nuevo_diagnostico = diagnostico_sel

            try:
                nueva_saturacion = int(entry_saturacion.get()) if entry_saturacion.get().strip() else None
                nueva_frecuencia = int(entry_frecuencia.get()) if entry_frecuencia.get().strip() else None
                nueva_temperatura = float(entry_temperatura.get()) if entry_temperatura.get().strip() else None
            except ValueError:
                messagebox.showwarning("Atención", "Saturación/Frecuencia deben ser enteros y Temperatura numérica.", parent=ventana)
                return

            nueva_recomendacion = textbox_recomendacion.get("1.0", "end").strip()

            actualizar_estudiante(estudiante_id, nuevo_nombre, nuevo_curso, nuevo_paralelo, nuevo_sexo)
            actualizar_atencion(
                id_atencion, nueva_saturacion, nueva_temperatura, nueva_frecuencia,
                nuevo_diagnostico, nueva_recomendacion
            )

            messagebox.showinfo("Éxito", "Atención actualizada correctamente.", parent=ventana)
            ventana.destroy()
            self._cargar_atenciones()

        frame_botones = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_botones.grid(row=18, column=0, columnspan=2, sticky="ew")
        frame_botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            frame_botones, text="Cancelar", fg_color=estilos.COLOR_AMARILLO, hover_color=estilos.COLOR_AMARILLO_HOVER,
            command=ventana.destroy
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(frame_botones, text="Guardar cambios", command=guardar).grid(
            row=0, column=1, padx=(5, 0), sticky="ew"
        )

    # ------------------------------------------------------------
    # Eliminar atención
    # ------------------------------------------------------------
    def _confirmar_eliminar(self, id_atencion, nombre, fecha):
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar la atención de '{nombre}' del {fecha}?\nEsta acción no se puede deshacer."
        )
        if not confirmar:
            return

        eliminar_atencion(id_atencion)
        messagebox.showinfo("Éxito", "Atención eliminada correctamente.")
        self._cargar_atenciones()