"""
app.py - Vista principal de la aplicación de Taller Mecánico.
Maneja la navegación, el control de acceso visual (RBAC) y el intercambio de vistas.
"""

import customtkinter as ctk
from core.auth import SesionManager
from views.views_auth import LoginView
from views.views_recepcion import ViewRecepcion
from views.views_mecanico import ViewMecanico
from views.views_finanzas import ViewFinanzas
from views.views_reportes import ViewReportes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class TallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Taller Mecánico")
        self.geometry("1100x680")
        self.resizable(False, False)

        self.sidebar = None 
        self.content_area = None

        self.mostrar_login()

    def limpiar_todo(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_todo()
        SesionManager.cerrar_sesion()
        login_view = LoginView(self, on_login_success=self.construir_dashboard)
        login_view.pack(expand=True, fill="both")

    def construir_dashboard(self):
        self.limpiar_todo()

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Área dinámica de contenido
        self.content_area = ctk.CTkFrame(self, corner_radius=0)
        self.content_area.pack(side="right", expand=True, fill="both")  

        rol = SesionManager.obtener_rol()
        user = SesionManager.usuario_actual["username"]

        lbl_logo = ctk.CTkLabel(self.sidebar, text="TALLER MOTOR", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_logo.pack(padx=20, pady=(20, 5))

        lbl_info = ctk.CTkLabel(self.sidebar, text=f"Usuario: {user}\nRol: {rol}", text_color="gray70", justify="center")
        lbl_info.pack(padx=20, pady=(0, 20))

        if rol in ["ADMIN", "RECEPCIONISTA (ventas)"]:
            ctk.CTkButton(self.sidebar, text="Recepción y Tareas", command=lambda: self.cambiar_vista(ViewRecepcion)).pack(padx=15, pady=8, fill="x")
            ctk.CTkButton(self.sidebar, text="Finanzas y Pagos", command=lambda: self.cambiar_vista(ViewFinanzas)).pack(padx=15, pady=8, fill="x")

        if rol in ["ADMIN", "MECANICO"]:
            ctk.CTkButton(self.sidebar, text="Panel Mecánico", command=lambda: self.cambiar_vista(ViewMecanico)).pack(padx=15, pady=8, fill="x")

        if rol == "ADMIN":
            ctk.CTkButton(self.sidebar, text="Reporte Matricial", fg_color="#2b7a4b", hover_color="#1e5835",
                          command=lambda: self.cambiar_vista(ViewReportes)).pack(padx=15, pady=8, fill="x")

        btn_salir = ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color="#912d2d", hover_color="#6e2020", command=self.mostrar_login)
        btn_salir.pack(side="bottom", padx=15, pady=20, fill="x")

        if rol == "MECANICO":
            self.cambiar_vista(ViewMecanico)
        else:
            self.cambiar_vista(ViewRecepcion)

    def cambiar_vista(self, VistaClase):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        nueva_vista = VistaClase(self.content_area)
        nueva_vista.pack(fill="both", expand=True)