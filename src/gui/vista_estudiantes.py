import customtkinter as ctk

class VistaEstudiantes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="Gestión de Estudiantes (en construcción)",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)