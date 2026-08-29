"""
Ventana de inicio de sesión. Permite iniciar sesión o crear una cuenta nueva
directamente ahí (sin necesitar un panel de administrador aparte).
Al iniciar sesión con éxito, guarda la sesión y cierra esta ventana.
"""

import customtkinter as ctk
from tkinter import messagebox
from gui import estilos

from database.consultas import existe_usuario, crear_usuario, obtener_usuario_por_usuario
from auth import (
    hash_password, verificar_password, guardar_sesion, establecer_usuario_actual,
    guardar_ultimo_usuario, cargar_ultimo_usuario, CODIGO_AUTORIZACION_CUENTAS
)

ANCHO_VENTANA = 380
ALTO_TAB_LOGIN = 420
ALTO_TAB_REGISTRO = 610


class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Iniciar sesión - Enfermería AMMI")
        self.geometry(f"{ANCHO_VENTANA}x{ALTO_TAB_LOGIN}")
        self.resizable(False, False)

        self.sesion_iniciada = False

        # --- Encabezado de bienvenida ---
        ctk.CTkLabel(
            self, text="🩺 Enfermería AMMI",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self, text="Ingresa tus credenciales para continuar",
            text_color=estilos.COLOR_TEXTO_GRIS
        ).pack(pady=(0, 10))

        # --- Tabview con estilo de pestañas de login ---
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="transparent",
            segmented_button_fg_color=estilos.COLOR_NEGRO_SUAVE,
            segmented_button_selected_color=estilos.COLOR_AMARILLO,
            segmented_button_selected_hover_color=estilos.COLOR_AMARILLO_HOVER,
            segmented_button_unselected_color=estilos.COLOR_NEGRO_SUAVE,
            segmented_button_unselected_hover_color=estilos.COLOR_NEGRO,
            command=self._on_cambiar_tab,
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tabview.add("Iniciar sesión")
        self.tabview.add("Crear cuenta")

        # Ajustes adicionales al segmented button interno (tamaño, tipografía, color de texto)
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(size=14, weight="bold"),
            height=36,
            corner_radius=8,
            text_color=("gray10", "gray90"),
            text_color_disabled=estilos.COLOR_TEXTO_GRIS,
        )

        self._crear_tab_login()
        self._crear_tab_registro()

    def _on_cambiar_tab(self):
        """Se dispara automáticamente al cambiar de pestaña; ajusta el alto de la
        ventana según cuánto contenido tiene cada una (Crear cuenta necesita más
        espacio por el campo extra de código de autorización)."""
        tab_actual = self.tabview.get()
        if tab_actual == "Crear cuenta":
            self.geometry(f"{ANCHO_VENTANA}x{ALTO_TAB_REGISTRO}")
        else:
            self.geometry(f"{ANCHO_VENTANA}x{ALTO_TAB_LOGIN}")

    # ------------------------------------------------------------
    # Tab: Iniciar sesión
    # ------------------------------------------------------------
    def _crear_tab_login(self):
        tab = self.tabview.tab("Iniciar sesión")

        ctk.CTkLabel(tab, text="Usuario", anchor="w").pack(fill="x", pady=(15, 0))
        self.entry_login_usuario = ctk.CTkEntry(tab)
        self.entry_login_usuario.pack(fill="x", pady=(0, 10))

        ultimo_usuario = cargar_ultimo_usuario()
        if ultimo_usuario:
            self.entry_login_usuario.insert(0, ultimo_usuario)

        ctk.CTkLabel(tab, text="Contraseña", anchor="w").pack(fill="x")
        self.entry_login_password = ctk.CTkEntry(tab, show="•")
        self.entry_login_password.pack(fill="x", pady=(0, 20))
        self.entry_login_password.bind("<Return>", lambda e: self._iniciar_sesion())

        if ultimo_usuario:
            self.entry_login_password.focus()  # el usuario ya está lleno, salta directo a la contraseña

        ctk.CTkButton(tab, text="Iniciar sesión", command=self._iniciar_sesion).pack(fill="x")

    def _iniciar_sesion(self):
        usuario = self.entry_login_usuario.get().strip()
        password = self.entry_login_password.get()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Ingresa usuario y contraseña.")
            return

        fila = obtener_usuario_por_usuario(usuario)
        if not fila:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        id_usuario, nombre_completo, _usuario, password_hash, rol, activo = fila

        if not activo:
            messagebox.showerror("Cuenta deshabilitada", "Esta cuenta está deshabilitada. Contacta al administrador.")
            return

        if not verificar_password(password, password_hash):
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        guardar_ultimo_usuario(usuario)
        guardar_sesion(id_usuario, nombre_completo)
        establecer_usuario_actual(id_usuario, nombre_completo)
        self.sesion_iniciada = True
        self.destroy()

    # ------------------------------------------------------------
    # Tab: Crear cuenta
    # ------------------------------------------------------------
    def _crear_tab_registro(self):
        tab = self.tabview.tab("Crear cuenta")

        ctk.CTkLabel(tab, text="Nombre completo", anchor="w").pack(fill="x", pady=(15, 0))
        self.entry_reg_nombre = ctk.CTkEntry(tab)
        self.entry_reg_nombre.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tab, text="Usuario", anchor="w").pack(fill="x")
        self.entry_reg_usuario = ctk.CTkEntry(tab)
        self.entry_reg_usuario.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tab, text="Contraseña", anchor="w").pack(fill="x")
        self.entry_reg_password = ctk.CTkEntry(tab, show="•")
        self.entry_reg_password.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tab, text="Confirmar contraseña", anchor="w").pack(fill="x")
        self.entry_reg_password2 = ctk.CTkEntry(tab, show="•")
        self.entry_reg_password2.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tab, text="Código de autorización", anchor="w").pack(fill="x")
        self.entry_reg_codigo = ctk.CTkEntry(tab, show="•")
        self.entry_reg_codigo.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(tab, text="Crear cuenta", command=self._crear_cuenta).pack(fill="x")

    def _crear_cuenta(self):
        nombre = self.entry_reg_nombre.get().strip()
        usuario = self.entry_reg_usuario.get().strip()
        password = self.entry_reg_password.get()
        password2 = self.entry_reg_password2.get()

        if not nombre or not usuario or not password:
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return
        if len(password) < 4:
            messagebox.showwarning("Atención", "La contraseña debe tener al menos 4 caracteres.")
            return
        if password != password2:
            messagebox.showwarning("Atención", "Las contraseñas no coinciden.")
            return

        codigo = self.entry_reg_codigo.get().strip()
        if codigo != CODIGO_AUTORIZACION_CUENTAS:
            messagebox.showerror("Código incorrecto", "El código de autorización no es válido.")
            return

        if existe_usuario(usuario):
            messagebox.showerror("Error", "Ese nombre de usuario ya existe, elige otro.")
            return

        password_hash = hash_password(password)
        id_usuario = crear_usuario(nombre, usuario, password_hash)

        messagebox.showinfo("Cuenta creada", "Cuenta creada correctamente. Ya puedes iniciar sesión.")
        guardar_sesion(id_usuario, nombre)
        establecer_usuario_actual(id_usuario, nombre)
        self.sesion_iniciada = True
        self.destroy()