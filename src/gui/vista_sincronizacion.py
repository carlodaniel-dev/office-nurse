import customtkinter as ctk

class VistaSincronizacion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="Sincronización de bases de datos (en construcción)",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)