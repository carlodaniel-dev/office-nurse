"""
Vista para registrar una nueva atención de enfermería.
Incluye autocompletado de estudiante por nombre.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from gui.constantes import CURSOS, PARALELOS, DIAGNOSTICOS

from database.consultas import (
    buscar_estudiantes_por_nombre,
    buscar_estudiante_exacto,
    crear_estudiante,
    crear_atencion,
    cerrar_atencion,
    listar_atenciones_por_fecha,
)

class VistaAtenciones(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.estudiante_seleccionado_id = None  # se llena al elegir una sugerencia

        self.grid_columnconfigure(0, weight=1)
        self._crear_widgets()
        self._cargar_atenciones_del_dia()

    def _crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="Registrar atención", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 15))

        frame_formulario = ctk.CTkFrame(self)
        frame_formulario.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame_formulario.grid_columnconfigure(0, weight=1)
        frame_formulario.grid_columnconfigure(1, weight=1)
        frame_formulario.grid_columnconfigure(2, weight=1)

        # --- Fila 1: Nombre Curso Paralelo ---
        ctk.CTkLabel(frame_formulario, text="Nombre *", anchor="w").grid(
            row=0, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.entry_nombre = ctk.CTkEntry(frame_formulario)
        self.entry_nombre.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="ew")
        self.entry_nombre.bind("<KeyRelease>", self._on_escribir_nombre)

        ctk.CTkLabel(frame_formulario, text="Curso *", anchor="w").grid(
            row=0, column=1, padx=10, pady=(10, 0), sticky="w"
        )
        self.combo_curso = ctk.CTkComboBox(frame_formulario, values=CURSOS, state="readonly")
        self.combo_curso.set("")
        self.combo_curso.grid(row=1, column=1, padx=10, pady=(0, 0), sticky="ew")

        ctk.CTkLabel(frame_formulario, text="Paralelo", anchor="w").grid(
            row=0, column=2, padx=10, pady=(10, 0), sticky="w"
        )
        self.combo_paralelo = ctk.CTkComboBox(frame_formulario, values=PARALELOS, state="readonly")
        self.combo_paralelo.set("")
        self.combo_paralelo.grid(row=1, column=2, padx=10, pady=(0, 0), sticky="ew")

        # Frame de sugerencias del nombre (debajo del campo Nombre)
        self.frame_sugerencias = ctk.CTkFrame(frame_formulario, fg_color=("gray90", "gray20"))

        # --- Fila 2: Saturación, Frecuencia, Temperatura ---
        ctk.CTkLabel(frame_formulario, text="Saturación (%)", anchor="w").grid(
            row=5, column=0, padx=10, pady=(0, 0), sticky="w"
        )
        self.entry_saturacion = ctk.CTkEntry(frame_formulario)
        self.entry_saturacion.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(frame_formulario, text="Frecuencia cardíaca (lpm)", anchor="w").grid(
            row=5, column=1, padx=10, pady=(0, 0), sticky="w"
        )
        self.entry_frecuencia = ctk.CTkEntry(frame_formulario)
        self.entry_frecuencia.grid(row=6, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(frame_formulario, text="Temperatura (°C)", anchor="w").grid(
            row=5, column=2, padx=10, pady=(0, 0), sticky="w"
        )
        self.entry_temperatura = ctk.CTkEntry(frame_formulario)
        self.entry_temperatura.grid(row=6, column=2, padx=10, pady=(0, 10), sticky="ew")

                # --- Fila 4: Diagnóstico + Sexo ---
        ctk.CTkLabel(frame_formulario, text="Diagnóstico *", anchor="w").grid(
            row=7, column=0, columnspan=2, padx=10, pady=(0, 0), sticky="w"
        )
        self.combo_diagnostico = ctk.CTkComboBox(
            frame_formulario, values=DIAGNOSTICOS, state="readonly",
            command=self._on_cambiar_diagnostico
        )
        self.combo_diagnostico.set("")
        self.combo_diagnostico.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(frame_formulario, text="Sexo *", anchor="w").grid(
            row=7, column=2, padx=10, pady=(0, 0), sticky="w"
        )
        self.var_sexo = ctk.StringVar(value="")
        self.segmented_sexo = ctk.CTkSegmentedButton(
            frame_formulario,
            values=["Masculino", "Femenino"],
            variable=self.var_sexo
        )
        self.segmented_sexo.grid(row=8, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Campo "Otros" para diagnóstico (ancho completo, su propia fila)
        self.entry_diagnostico_otro = ctk.CTkEntry(frame_formulario, placeholder_text="Especifique el diagnóstico")
        self.entry_diagnostico_otro.grid(row=9, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        self.entry_diagnostico_otro.grid_remove()

        # --- Fila 5: Recomendación (ancho completo) ---
        ctk.CTkLabel(frame_formulario, text="Recomendación", anchor="w").grid(
            row=10, column=0, columnspan=3, padx=10, pady=(0, 0), sticky="w"
        )
        self.textbox_recomendacion = ctk.CTkTextbox(frame_formulario, height=60)
        self.textbox_recomendacion.grid(row=11, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

        # --- Botón guardar ---
        btn_guardar = ctk.CTkButton(self, text="Guardar atención", command=self._guardar_atencion)
        btn_guardar.grid(row=2, column=0, sticky="w", pady=(0, 20))

        # --- Tabla de atenciones del día ---
        titulo_tabla = ctk.CTkLabel(self, text="Atenciones de hoy", font=ctk.CTkFont(size=16, weight="bold"))
        titulo_tabla.grid(row=3, column=0, sticky="w", pady=(0, 10))

        self.frame_tabla = ctk.CTkScrollableFrame(self, height=200)
        self.frame_tabla.grid(row=4, column=0, sticky="nsew")
        self.frame_tabla.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    
    # ------------------------------------------------------------
    # Autocompletado de nombre
    # ------------------------------------------------------------
    def _on_escribir_nombre(self, event=None):
        # Si el usuario sigue editando el nombre, invalidamos cualquier selección previa
        self.estudiante_seleccionado_id = None

        texto = self.entry_nombre.get().strip()
        for widget in self.frame_sugerencias.winfo_children():
            widget.destroy()

        if len(texto) < 2:
            self.frame_sugerencias.grid_forget()
            return

        resultados = buscar_estudiantes_por_nombre(texto)
        if not resultados:
            self.frame_sugerencias.grid_forget()
            return

        for id_est, nombre, curso, paralelo, sexo in resultados:
            texto_paralelo = f" {paralelo}" if paralelo and paralelo != "N/A" else ""
            boton = ctk.CTkButton(
                self.frame_sugerencias,
                text=f"{nombre}  —  {curso}{texto_paralelo}",
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray30"),
                command=lambda i=id_est, n=nombre, c=curso, p=paralelo, s=sexo: self._seleccionar_sugerencia(i, n, c, p)
            )
            boton.pack(fill="x", padx=2, pady=2)

        self.frame_sugerencias.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _seleccionar_sugerencia(self, id_estudiante, nombre, curso, paralelo, sexo):
        self.estudiante_seleccionado_id = id_estudiante
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, nombre)
        self.combo_curso.set(curso)
        self.combo_paralelo.set(paralelo or "")
        self.var_sexo.set(sexo or "")
        self.frame_sugerencias.grid_forget()
    
    def _on_cambiar_diagnostico(self, valor_seleccionado):
        if valor_seleccionado == "Otros":
            self.entry_diagnostico_otro.grid()
            self.entry_diagnostico_otro.focus()
        else:
            self.entry_diagnostico_otro.grid_remove()
            self.entry_diagnostico_otro.delete(0, "end")

    # ------------------------------------------------------------
    # Guardar atención
    # ------------------------------------------------------------
    def _guardar_atencion(self):
        nombre = self.entry_nombre.get().strip()
        curso = self.combo_curso.get().strip()
        paralelo = self.combo_paralelo.get().strip()
        sexo = self.var_sexo.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if not curso:
            messagebox.showwarning("Atención", "Selecciona el curso.")
            return
        if not paralelo:
            messagebox.showwarning("Atención", "Selecciona el paralelo.")
            return
        if not sexo:
            messagebox.showwarning("Atención", "Selecciona el sexo.")
            return
            return

        # Validaciones numéricas simples (campos opcionales, pero si se llenan deben ser válidos)
        saturacion = self._validar_entero(self.entry_saturacion.get(), "Saturación")
        frecuencia = self._validar_entero(self.entry_frecuencia.get(), "Frecuencia cardíaca")
        temperatura = self._validar_decimal(self.entry_temperatura.get(), "Temperatura")
        if saturacion is False or frecuencia is False or temperatura is False:
            return  # el mensaje de error ya se mostró dentro del validador

        # Resolver el estudiante: usar el seleccionado, o buscar coincidencia exacta, o crear nuevo
        estudiante_id = self.estudiante_seleccionado_id
        if not estudiante_id:
            estudiante_id = buscar_estudiante_exacto(nombre, curso, paralelo)
        if not estudiante_id:
            estudiante_id = crear_estudiante(nombre, curso, paralelo, sexo)

        diagnostico_seleccionado = self.combo_diagnostico.get().strip()
        if not diagnostico_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un diagnóstico.")
            return

        if diagnostico_seleccionado == "Otros":
            diagnostico = self.entry_diagnostico_otro.get().strip()
            if not diagnostico:
                messagebox.showwarning("Atención", "Especifica el diagnóstico en el campo de texto.")
                return
        else:
            diagnostico = diagnostico_seleccionado
        recomendacion = self.textbox_recomendacion.get("1.0", "end").strip()

        crear_atencion(
            estudiante_id=estudiante_id,
            saturacion=saturacion,
            temperatura=temperatura,
            frecuencia_cardiaca=frecuencia,
            diagnostico=diagnostico,
            recomendacion=recomendacion,
        )

        messagebox.showinfo("Éxito", "Atención registrada correctamente.")
        self._limpiar_formulario()
        self._cargar_atenciones_del_dia()

    def _validar_entero(self, valor, nombre_campo):
        valor = valor.strip()
        if not valor:
            return None
        try:
            return int(valor)
        except ValueError:
            messagebox.showwarning("Atención", f"'{nombre_campo}' debe ser un número entero.")
            return False

    def _validar_decimal(self, valor, nombre_campo):
        valor = valor.strip()
        if not valor:
            return None
        try:
            return float(valor)
        except ValueError:
            messagebox.showwarning("Atención", f"'{nombre_campo}' debe ser un número (ej. 36.5).")
            return False

    def _limpiar_formulario(self):
        self.entry_nombre.delete(0, "end")
        self.combo_curso.set("")
        self.combo_paralelo.set("")
        self.var_sexo.set("")
        self.entry_saturacion.delete(0, "end")
        self.entry_frecuencia.delete(0, "end")
        self.entry_temperatura.delete(0, "end")
        self.combo_diagnostico.set("")
        self.entry_diagnostico_otro.delete(0, "end")
        self.entry_diagnostico_otro.grid_forget()
        self.textbox_recomendacion.delete("1.0", "end")
        self.estudiante_seleccionado_id = None
        self.frame_sugerencias.grid_remove()

    # ------------------------------------------------------------
    # Tabla de atenciones del día
    # ------------------------------------------------------------
    def _cargar_atenciones_del_dia(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        hoy = datetime.now().strftime("%Y-%m-%d")
        atenciones = listar_atenciones_por_fecha(hoy)

        encabezados = ["Hora llegada", "Estudiante", "Curso", "Paralelo", "Hora salida"]
        for i, texto in enumerate(encabezados):
            ctk.CTkLabel(self.frame_tabla, text=texto, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="w"
            )

        if not atenciones:
            ctk.CTkLabel(self.frame_tabla, text="Sin atenciones registradas hoy.", text_color="gray").grid(
                row=1, column=0, columnspan=4, padx=5, pady=10, sticky="w"
            )
            return

        # atenciones: columnas de 'atenciones' (a.*) + nombre, paralelo al final
        for fila_idx, atencion in enumerate(atenciones, start=1):
            id_atencion = atencion[0]
            hora_llegada = atencion[3]
            hora_salida = atencion[4]
            nombre = atencion[-3]
            curso = atencion[-2]
            paralelo = atencion[-1]

            ctk.CTkLabel(self.frame_tabla, text=hora_llegada).grid(row=fila_idx, column=0, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.frame_tabla, text=nombre).grid(row=fila_idx, column=1, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.frame_tabla, text=curso).grid(row=fila_idx, column=2, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.frame_tabla, text=paralelo).grid(row=fila_idx, column=3, padx=5, pady=3, sticky="w")

            if hora_salida:
                ctk.CTkLabel(self.frame_tabla, text=hora_salida).grid(row=fila_idx, column=3, padx=5, pady=3, sticky="w")
            else:
                btn_salida = ctk.CTkButton(
                    self.frame_tabla, text="Marcar salida", width=110, height=24,
                    command=lambda i=id_atencion: self._marcar_salida(i)
                )
                btn_salida.grid(row=fila_idx, column=3, padx=5, pady=3, sticky="w")
            
            btn_detalle = ctk.CTkButton(
                self.frame_tabla, text="Ver detalle", width=100, height=24,
                fg_color="gray40", hover_color="gray30",
                command=lambda a=atencion: self._mostrar_detalle_atencion(a)
            )
            btn_detalle.grid(row=fila_idx, column=4, padx=5, pady=3, sticky="w")

    def _mostrar_detalle_atencion(self, atencion):
            """Abre una ventana emergente con todos los datos de la atención."""
            saturacion = atencion[5]
            temperatura = atencion[6]
            frecuencia = atencion[7]
            diagnostico = atencion[8]
            recomendacion = atencion[9]
            nombre = atencion[-3]
            curso = atencion[-2]
            paralelo = atencion[-1]

            ventana = ctk.CTkToplevel(self)
            ventana.title(f"Detalle - {nombre}")
            ventana.geometry("420x420")
            ventana.grab_set()  # bloquea la ventana principal hasta que se cierre esta

            contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
            contenedor.pack(fill="both", expand=True, padx=20, pady=20)

            def agregar_campo(etiqueta, valor):
                ctk.CTkLabel(contenedor, text=etiqueta, font=ctk.CTkFont(weight="bold"), anchor="w").pack(
                    fill="x", pady=(8, 0)
                )
                ctk.CTkLabel(contenedor, text=valor or "—", anchor="w", justify="left", wraplength=370).pack(
                    fill="x", pady=(0, 0)
                )

            agregar_campo("Estudiante", f"{nombre} — {curso} {paralelo or ''}".strip())
            agregar_campo("Saturación", f"{saturacion}%" if saturacion is not None else "—")
            agregar_campo("Frecuencia cardíaca", f"{frecuencia} lpm" if frecuencia is not None else "—")
            agregar_campo("Temperatura", f"{temperatura} °C" if temperatura is not None else "—")
            agregar_campo("Diagnóstico", diagnostico)
            agregar_campo("Recomendación", recomendacion)

            btn_cerrar = ctk.CTkButton(contenedor, text="Cerrar", command=ventana.destroy)
            btn_cerrar.pack(pady=(20, 0))

    def _marcar_salida(self, id_atencion):
        cerrar_atencion(id_atencion)
        self._cargar_atenciones_del_dia()