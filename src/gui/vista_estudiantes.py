"""
Vista de gestión del catálogo de estudiantes: ver, buscar, editar y eliminar.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.consultas import (
    listar_estudiantes,
    filtrar_estudiantes,
    actualizar_estudiante,
    eliminar_estudiante,
)

from gui.constantes import CURSOS, PARALELOS


class VistaEstudiantes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._crear_widgets()
        self._cargar_estudiantes()

    def _crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="Estudiantes", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Buscador ---
        frame_buscador = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscador.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        frame_buscador.grid_columnconfigure(0, weight=1)

        self.entry_buscar = ctk.CTkEntry(frame_buscador, placeholder_text="Buscar por nombre, curso o paralelo...")
        self.entry_buscar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_estudiantes())

        self.label_total = ctk.CTkLabel(frame_buscador, text="", text_color="gray")
        self.label_total.grid(row=0, column=1, sticky="e")

        # --- Encabezados de la tabla ---
        frame_encabezados = ctk.CTkFrame(self)
        frame_encabezados.grid(row=2, column=0, sticky="new")
        for i, ancho in enumerate([3, 2, 1, 2]):
            frame_encabezados.grid_columnconfigure(i, weight=ancho)
        frame_encabezados.grid_columnconfigure(4, weight=0)

        encabezados = ["Nombre", "Curso", "Paralelo", "Sexo"]
        for i, texto in enumerate(encabezados):
            ctk.CTkLabel(frame_encabezados, text=texto, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=10, pady=8, sticky="w"
            )

        # --- Tabla scrollable ---
        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_tabla.grid(row=3, column=0, sticky="nsew")
        for i, ancho in enumerate([3, 2, 1, 2]):
            self.frame_tabla.grid_columnconfigure(i, weight=ancho)
        self.frame_tabla.grid_columnconfigure(4, weight=0)
        self.grid_rowconfigure(3, weight=1)

    def _cargar_estudiantes(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        texto = self.entry_buscar.get().strip()
        estudiantes = filtrar_estudiantes(texto) if texto else listar_estudiantes()

        self.label_total.configure(text=f"{len(estudiantes)} estudiante(s)")

        if not estudiantes:
            ctk.CTkLabel(self.frame_tabla, text="No se encontraron estudiantes.", text_color="gray").grid(
                row=0, column=0, columnspan=5, padx=10, pady=20, sticky="w"
            )
            return

        # estudiantes: id, nombre, curso, paralelo, sexo, origen_pc, fecha_creacion
        for fila_idx, est in enumerate(estudiantes):
            id_est, nombre, curso, paralelo, sexo = est[0], est[1], est[2], est[3], est[4]

            ctk.CTkLabel(self.frame_tabla, text=nombre, anchor="w").grid(
                row=fila_idx, column=0, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=curso, anchor="w").grid(
                row=fila_idx, column=1, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=paralelo or "—", anchor="w").grid(
                row=fila_idx, column=2, padx=10, pady=6, sticky="w"
            )
            ctk.CTkLabel(self.frame_tabla, text=sexo or "—", anchor="w").grid(
                row=fila_idx, column=3, padx=10, pady=6, sticky="w"
            )

            frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
            frame_acciones.grid(row=fila_idx, column=4, padx=10, pady=4, sticky="e")

            btn_editar = ctk.CTkButton(
                frame_acciones, text="Editar", width=70, height=26,
                command=lambda e=est: self._abrir_editor(e)
            )
            btn_editar.pack(side="left", padx=(0, 6))

            btn_eliminar = ctk.CTkButton(
                frame_acciones, text="Eliminar", width=70, height=26,
                fg_color="#B3261E", hover_color="#8C1D18",
                command=lambda i=id_est, n=nombre: self._confirmar_eliminar(i, n)
            )
            btn_eliminar.pack(side="left")

    # ------------------------------------------------------------
    # Editar estudiante
    # ------------------------------------------------------------
    def _abrir_editor(self, estudiante):
        id_est, nombre, curso, paralelo, sexo = estudiante[0], estudiante[1], estudiante[2], estudiante[3], estudiante[4]

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar estudiante")
        ventana.geometry("420x340")
        ventana.grab_set()

        contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)

        # --- Nombre (ancho completo) ---
        ctk.CTkLabel(contenedor, text="Nombre", anchor="w").grid(
            row=0, column=0, columnspan=2, pady=(0, 0), sticky="w"
        )
        entry_nombre = ctk.CTkEntry(contenedor)
        entry_nombre.insert(0, nombre)
        entry_nombre.grid(row=1, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        # --- Curso + Paralelo (misma fila) ---
        ctk.CTkLabel(contenedor, text="Curso", anchor="w").grid(
            row=2, column=0, padx=(0, 5), pady=(0, 0), sticky="w"
        )
        combo_curso = ctk.CTkComboBox(contenedor, values=CURSOS, state="readonly")
        combo_curso.set(curso)
        combo_curso.grid(row=3, column=0, padx=(0, 5), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(contenedor, text="Paralelo", anchor="w").grid(
            row=2, column=1, padx=(5, 0), pady=(0, 0), sticky="w"
        )
        combo_paralelo = ctk.CTkComboBox(contenedor, values=PARALELOS, state="readonly")
        combo_paralelo.set(paralelo or "")
        combo_paralelo.grid(row=3, column=1, padx=(5, 0), pady=(0, 12), sticky="ew")

        # --- Sexo (ancho completo, pero el widget centrado) ---
        ctk.CTkLabel(contenedor, text="Sexo", anchor="w").grid(
            row=4, column=0, columnspan=2, pady=(0, 0), sticky="w"
        )
        var_sexo = ctk.StringVar(value=sexo or "")
        segmented_sexo = ctk.CTkSegmentedButton(contenedor, values=["Masculino", "Femenino"], variable=var_sexo)
        segmented_sexo.grid(row=5, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        def guardar():
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_curso = combo_curso.get().strip()
            nuevo_paralelo = combo_paralelo.get().strip()
            nuevo_sexo = var_sexo.get().strip()

            if not nuevo_nombre or not nuevo_curso or not nuevo_paralelo or not nuevo_sexo:
                messagebox.showwarning("Atención", "Todos los campos son obligatorios.", parent=ventana)
                return

            actualizar_estudiante(id_est, nuevo_nombre, nuevo_curso, nuevo_paralelo, nuevo_sexo)
            messagebox.showinfo("Éxito", "Estudiante actualizado correctamente.", parent=ventana)
            ventana.destroy()
            self._cargar_estudiantes()

        # --- Botones ---
        frame_botones = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_botones.grid(row=6, column=0, columnspan=2, sticky="ew")
        frame_botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(frame_botones, text="Cancelar", fg_color="gray40", hover_color="gray30",
                    command=ventana.destroy).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(frame_botones, text="Guardar cambios", command=guardar).grid(
            row=0, column=1, padx=(5, 0), sticky="ew"
        )

    # ------------------------------------------------------------
    # Eliminar estudiante
    # ------------------------------------------------------------
    def _confirmar_eliminar(self, id_estudiante, nombre):
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar a '{nombre}' del catálogo?\nEsta acción no se puede deshacer."
        )
        if not confirmar:
            return

        exito, motivo = eliminar_estudiante(id_estudiante)
        if exito:
            messagebox.showinfo("Éxito", "Estudiante eliminado correctamente.")
        else:
            messagebox.showerror("No se pudo eliminar", motivo)

        self._cargar_estudiantes()