"""
Vista de Reportes: gráficas de atenciones por mes.
- Tendencia mensual (todas las atenciones, línea)
- Diagnósticos más frecuentes del mes seleccionado (barras)
- Atenciones por curso del mes seleccionado, separado EGB / Bachillerato (barras)
- Sección filtrable: tendencia y diagnósticos de un curso+paralelo específico
"""

import customtkinter as ctk
from gui import estilos

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

from database.consultas import (
    listar_meses_disponibles,
    contar_atenciones_por_mes,
    contar_diagnosticos_por_mes,
    contar_atenciones_por_curso_mes,
    contar_atenciones_por_especialidad_mes,
    contar_atenciones_por_mes_filtrado,
    contar_diagnosticos_por_mes_filtrado,
)
from gui.constantes import (
    CURSOS, PARALELOS, DIAGNOSTICOS,
    CURSOS_EGB, CURSOS_BACHILLERATO, PARALELOS_EGB, ESPECIALIDADES_BACHILLERATO, ESPECIALIDADES_ABREVIADAS,
)

MESES_ES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
}


def _nombre_mes(mes_iso):
    """Convierte '2026-08' en 'Agosto 2026'."""
    anio, mes = mes_iso.split("-")
    return f"{MESES_ES.get(mes, mes)} {anio}"


class VistaReportes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._crear_widgets()
        self._cargar_datos()

    def _crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="Reportes", font=estilos.fuente_titulo())
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Selector de mes (para las gráficas generales) ---
        frame_filtro = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtro.grid(row=1, column=0, sticky="w", pady=(0, 15))

        ctk.CTkLabel(frame_filtro, text="Mes:", anchor="w").pack(side="left", padx=(0, 10))
        self.combo_mes = ctk.CTkComboBox(
            frame_filtro, values=["—"], state="readonly", width=180,
            command=lambda _: self._cargar_datos()
        )
        self.combo_mes.pack(side="left")

        # --- Contenedor scrollable para las gráficas ---
        self.frame_contenido = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_contenido.grid(row=2, column=0, sticky="nsew")
        self.frame_contenido.grid_columnconfigure((0, 1), weight=1)

    def _cargar_datos(self):
        # --- Refresca la lista de meses disponibles ---
        meses = listar_meses_disponibles()
        if not meses:
            for widget in self.frame_contenido.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.frame_contenido, text="Todavía no hay atenciones registradas para generar reportes.",
                text_color=estilos.COLOR_TEXTO_GRIS
            ).grid(row=0, column=0, columnspan=2, padx=10, pady=30)
            return

        etiquetas_meses = [_nombre_mes(m) for m in meses]
        mapa_mes = dict(zip(etiquetas_meses, meses))

        mes_actual = self.combo_mes.get()
        if mes_actual not in etiquetas_meses:
            mes_actual = etiquetas_meses[0]  # el más reciente

        self.combo_mes.configure(values=etiquetas_meses)
        self.combo_mes.set(mes_actual)
        mes_iso = mapa_mes[mes_actual]

        # --- Limpia gráficas anteriores ---
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

        # --- 1. Sección filtrable por Curso + Paralelo (va primero) ---
        self._crear_seccion_filtro_curso_paralelo(row=0)

        # --- 2. Tendencia mensual (todas las atenciones, línea) ---
        datos_tendencia = contar_atenciones_por_mes()
        etiquetas_tendencia = [_nombre_mes(m) for m, _ in datos_tendencia]
        valores_tendencia = [total for _, total in datos_tendencia]
        self._crear_grafica_linea(
            "Tendencia de Atenciones por Mes", etiquetas_tendencia, valores_tendencia,
            row=1, columnspan=2
        )

        # --- 3. Diagnósticos más frecuentes del mes seleccionado ---
        diagnosticos_predefinidos = [d for d in DIAGNOSTICOS if d != "Otros"]
        datos_diagnosticos = contar_diagnosticos_por_mes(mes_iso, diagnosticos_predefinidos)
        self._crear_grafica_barras(
            f"Diagnósticos más Frecuentes — {mes_actual}",
            [d for d, _ in datos_diagnosticos], [t for _, t in datos_diagnosticos],
            row=2, column=0, columnspan=2, horizontal=True
        )

        # --- 4. Atenciones por curso EGB y Bachillerato, lado a lado en la misma fila ---
        datos_curso = dict(contar_atenciones_por_curso_mes(mes_iso))

        etiquetas_egb = CURSOS_EGB
        valores_egb = [datos_curso.get(c, 0) for c in CURSOS_EGB]
        self._crear_grafica_barras(
            f"Atenciones EGB — {mes_actual}",
            etiquetas_egb, valores_egb, row=3, column=0, columnspan=1, horizontal=False
        )

        datos_especialidad = {
            (curso, paralelo): total
            for curso, paralelo, total in contar_atenciones_por_especialidad_mes(mes_iso)
        }

        etiquetas_bach = []
        valores_bach = []
        for curso in CURSOS_BACHILLERATO:
            for especialidad in ESPECIALIDADES_BACHILLERATO:
                abrev = ESPECIALIDADES_ABREVIADAS.get(especialidad, especialidad)
                etiquetas_bach.append(f"{curso}\n{abrev}")
                valores_bach.append(datos_especialidad.get((curso, especialidad), 0))

        self._crear_grafica_barras(
            f"Atenciones Bachillerato — {mes_actual}",
            etiquetas_bach, valores_bach, row=3, column=1, columnspan=1, horizontal=False
        )
        
    # ------------------------------------------------------------
    # Sección: filtro por Curso + Paralelo específico
    # ------------------------------------------------------------
    def _crear_seccion_filtro_curso_paralelo(self, row):
        tarjeta = ctk.CTkFrame(self.frame_contenido)
        tarjeta.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=8)
        tarjeta.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            tarjeta, text="Ver por curso y paralelo específico", font=estilos.fuente_seccion_pequena()
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(tarjeta, text="Curso", anchor="w").grid(row=1, column=0, padx=15, sticky="w")
        self.combo_curso_filtro = ctk.CTkComboBox(
            tarjeta, values=CURSOS, state="readonly", command=self._on_cambiar_curso_filtro
        )
        self.combo_curso_filtro.set("")
        self.combo_curso_filtro.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(tarjeta, text="Paralelo", anchor="w").grid(row=1, column=1, padx=15, sticky="w")
        self.combo_paralelo_filtro = ctk.CTkComboBox(
            tarjeta, values=["Selecciona un curso primero"], state="disabled",
            command=lambda _: self._actualizar_graficas_filtro()
        )
        self.combo_paralelo_filtro.set("Selecciona un curso primero")
        self.combo_paralelo_filtro.grid(row=2, column=1, padx=15, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(tarjeta, text="Mes", anchor="w").grid(row=1, column=2, padx=15, sticky="w")
        meses = listar_meses_disponibles()
        etiquetas_meses = [_nombre_mes(m) for m in meses] or ["—"]
        self.combo_mes_filtro = ctk.CTkComboBox(
            tarjeta, values=etiquetas_meses, state="readonly",
            command=lambda _: self._actualizar_graficas_filtro()
        )
        self.combo_mes_filtro.set(etiquetas_meses[0])
        self.combo_mes_filtro.grid(row=2, column=2, padx=15, pady=(0, 15), sticky="ew")

        # Contenedor donde se dibujan las 2 gráficas filtradas (se regenera cada vez)
        self.frame_graficas_filtro = ctk.CTkFrame(tarjeta, fg_color="transparent")
        self.frame_graficas_filtro.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 10))
        self.frame_graficas_filtro.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.frame_graficas_filtro, text="Selecciona un curso y paralelo para ver sus gráficas.",
            text_color=estilos.COLOR_TEXTO_GRIS
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=20)

    def _on_cambiar_curso_filtro(self, curso_seleccionado):
        """Actualiza las opciones de Paralelo según el curso elegido (mismo criterio que el formulario)."""
        if curso_seleccionado in CURSOS_BACHILLERATO:
            nuevas_opciones = ESPECIALIDADES_BACHILLERATO
        elif curso_seleccionado in CURSOS_EGB:
            nuevas_opciones = PARALELOS_EGB
        else:
            nuevas_opciones = PARALELOS

        self.combo_paralelo_filtro.configure(values=nuevas_opciones, state="readonly")
        self.combo_paralelo_filtro.set(nuevas_opciones[0])
        self._actualizar_graficas_filtro()

    def _actualizar_graficas_filtro(self):
        curso = self.combo_curso_filtro.get().strip()
        paralelo = self.combo_paralelo_filtro.get().strip()

        for widget in self.frame_graficas_filtro.winfo_children():
            widget.destroy()

        if not curso or not paralelo or paralelo == "Selecciona un curso primero":
            ctk.CTkLabel(
                self.frame_graficas_filtro, text="Selecciona un curso y paralelo para ver sus gráficas.",
                text_color=estilos.COLOR_TEXTO_GRIS
            ).grid(row=0, column=0, columnspan=2, padx=10, pady=20)
            return

        etiqueta_mes = self.combo_mes_filtro.get()
        meses = listar_meses_disponibles()
        mapa_mes = {_nombre_mes(m): m for m in meses}
        mes_iso = mapa_mes.get(etiqueta_mes)

        # --- Tendencia mensual filtrada ---
        datos_tendencia = contar_atenciones_por_mes_filtrado(curso, paralelo)
        etiquetas_tendencia = [_nombre_mes(m) for m, _ in datos_tendencia]
        valores_tendencia = [total for _, total in datos_tendencia]
        self._crear_grafica_linea(
            f"Tendencia — {curso} {paralelo}", etiquetas_tendencia, valores_tendencia,
            row=0, columnspan=1, master=self.frame_graficas_filtro, column=0
        )

        # --- Diagnósticos más frecuentes filtrados ---
        if mes_iso:
            diagnosticos_predefinidos = [d for d in DIAGNOSTICOS if d != "Otros"]
            datos_diagnosticos = contar_diagnosticos_por_mes_filtrado(
                mes_iso, curso, paralelo, diagnosticos_predefinidos
            )
            self._crear_grafica_barras(
                f"Diagnósticos — {curso} {paralelo} ({etiqueta_mes})",
                [d for d, _ in datos_diagnosticos], [t for _, t in datos_diagnosticos],
                row=0, column=1, horizontal=True, master=self.frame_graficas_filtro
            )

    # ------------------------------------------------------------
    # Helpers para crear gráficas embebidas con el estilo del sistema
    # ------------------------------------------------------------
    def _figura_base(self, figsize):
        fig = Figure(figsize=figsize, dpi=100)
        fig.patch.set_facecolor(estilos.COLOR_NEGRO_SUAVE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(estilos.COLOR_NEGRO_SUAVE)
        ax.tick_params(colors="#F5F5F5", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#555555")
        return fig, ax

    def _crear_grafica_linea(self, titulo, etiquetas, valores, row, columnspan=1, master=None, column=0):
        master = master or self.frame_contenido
        tarjeta = ctk.CTkFrame(master)
        tarjeta.grid(row=row, column=column, columnspan=columnspan, sticky="ew", padx=5, pady=8)

        ctk.CTkLabel(tarjeta, text=titulo, font=estilos.fuente_seccion_pequena()).pack(pady=(10, 5))

        if not valores:
            ctk.CTkLabel(tarjeta, text="Sin datos.", text_color=estilos.COLOR_TEXTO_GRIS).pack(pady=20)
            return

        fig, ax = self._figura_base(figsize=(9, 3) if master is self.frame_contenido else (5, 3))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.plot(etiquetas, valores, marker="o", color=estilos.COLOR_AMARILLO, linewidth=2)
        fig.autofmt_xdate(rotation=30)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tarjeta)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_grafica_barras(self, titulo, etiquetas, valores, row, column, columnspan=1, horizontal=False, master=None):
        master = master or self.frame_contenido
        tarjeta = ctk.CTkFrame(master)
        tarjeta.grid(row=row, column=column, columnspan=columnspan, sticky="ew", padx=5, pady=8)

        ctk.CTkLabel(tarjeta, text=titulo, font=estilos.fuente_seccion_pequena()).pack(pady=(10, 5))

        if not valores or sum(valores) == 0:
            ctk.CTkLabel(tarjeta, text="Sin datos para este mes.", text_color=estilos.COLOR_TEXTO_GRIS).pack(pady=20)
            return

        fig, ax = self._figura_base(figsize=(6, 3.2) if master is self.frame_contenido else (5, 3.2))
        if horizontal:
            ax.barh(etiquetas, valores, color=estilos.COLOR_AMARILLO)
            ax.invert_yaxis()
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            ax.bar(etiquetas, valores, color=estilos.COLOR_AMARILLO)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tarjeta)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))