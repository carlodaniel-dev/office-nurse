"""
Ventana de inicio de sesión. Permite iniciar sesión o crear una cuenta nueva
directamente ahí (sin necesitar un panel de administrador aparte).
Al iniciar sesión con éxito, guarda la sesión (8 horas) y cierra esta ventana.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.consultas import existe_usuario, crear_usuario, obtener_usuario_por_usuario
from auth import (
    hash_password, verificar_password, guardar_sesion, establecer_usuario_actual,
    guardar_ultimo_usuario, cargar_ultimo_usuario,
)


class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Iniciar sesión - Enfermería AMMI")
        self.geometry("380x420")
        self.resizable(False, False)

        self.sesion_iniciada = False

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabview.add("Iniciar sesión")
        self.tabview.add("Crear cuenta")

        self._crear_tab_login()
        self._crear_tab_registro()

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
        self.entry_reg_password2.pack(fill="x", pady=(0, 20))

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