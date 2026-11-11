"""
app.py - Vista principal de la aplicación de Taller Mecánico.
Maneja la navegación, el control de acceso visual (RBAC) y el intercambio de vistas.
"""

import customtkinter as ctk
from core.auth import SesionManager
from views.views_auth import LoginView, RegistroUsuarioView
from views.views_recepcion import ViewRecepcion
from views.views_mecanico import ViewMecanico
from views.views_finanzas import ViewFinanzas
from views.views_reportes import ViewReportes

# Configuración de apariencia global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BG_APP = "#0a0c1b"         # Fondo general profundo
BG_SIDEBAR = "#0e1126"     # Sidebar lateral
BG_CARD = "#14172f"        # Contenedores, tarjetas y navbar
BORDER_COLOR = "#1f2448"   # Líneas sutiles de relieve y separación
ACCENT_CYAN = "#00e5ff"    # Resalte activo e iluminado
ACCENT_PINK = "#ff3366"    # Alertas o acciones secundarias
TEXT_WHITE = "#ffffff"     # Texto principal
TEXT_MUTED = "#7a82a6"    # Texto secundario / subtítulos

class TallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Taller Motor - Sistema Integral de Gestión")
        self.geometry("1280x760")
        self.minsize(1080, 650)
        self.configure(fg_color=BG_APP)

        self.vista_activa = None
        self.botones_nav = {}

        #contenedor raiz donde se montan Login o la estructura del Dashboard
        self.root_container = ctk.CTkFrame(self, fg_color="transparent")
        self.root_container.pack(fill="both", expand=True)

        self.mostrar_login()

    def limpiar_pantalla(self):
        """Limpia los widgets internos sin destruir el root_container."""
        for widget in self.root_container.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        """Muestra la pantalla de inicio de sesión."""
        self.limpiar_pantalla()
        vista_login = LoginView(self.root_container, on_login_success=self.cargar_dashboard)
        vista_login.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        """Cierra la sesión activa y retorna al login."""
        SesionManager.cerrar_sesion()
        self.mostrar_login()

    def cargar_dashboard(self):
        """Construye el layout moderno con Sidebar + Navbar + Content Area."""
        self.limpiar_pantalla()
        self.botones_nav.clear()

        rol = SesionManager.obtener_rol()
        user_info = getattr(SesionManager, "usuario_actual", {}) or {}
        username = user_info.get("username", "Operador")


        """sidebar izquierdo"""

        sidebar = ctk.CTkFrame(
            self.root_container, 
            width=75, 
            corner_radius=0, 
            fg_color=BG_SIDEBAR, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        #Logo
        lbl_logo = ctk.CTkLabel(
            sidebar, 
            text="⚡", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color=ACCENT_CYAN
        )
        lbl_logo.pack(pady=(22, 25))

        """Contenido a la derecha"""
        main_area = ctk.CTkFrame(self.root_container, fg_color="transparent")
        main_area.pack(side="right", fill="both", expand=True)

        #barra de navegacion
        navbar = ctk.CTkFrame(
            main_area, 
            height=64, 
            corner_radius=0, 
            fg_color=BG_SIDEBAR, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        #barra de busqueda
        search_box = ctk.CTkEntry(
            navbar, 
            placeholder_text="🔍  Buscar por orden, patente, cliente...", 
            width=340, 
            height=36,
            corner_radius=18,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR,
            text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED
        )
        search_box.pack(side="left", padx=25, pady=14)

        #boton de cerrar sesion
        btn_logout = ctk.CTkButton(
            navbar,
            text="Salir",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#361725",
            hover_color="#521b33",
            text_color=ACCENT_PINK,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.cerrar_sesion
        )
        btn_logout.pack(side="right", padx=(10, 25), pady=16)

        #usuario y rol
        lbl_user = ctk.CTkLabel(
            navbar, 
            text=f"👤 {username}  •  {rol}", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_user.pack(side="right", padx=10, pady=16)

        self.lbl_modulo_actual = ctk.CTkLabel(
            navbar,
            text="PANEL PRINCIPAL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_WHITE
        )
        self.lbl_modulo_actual.pack(side="left", padx=20, pady=16)

        #Área de contenido central
        self.content_area = ctk.CTkFrame(main_area, fg_color="transparent")
        self.content_area.pack(side="bottom", fill="both", expand=True, padx=25, pady=20)

        #Rutas y navegacion dependiendo de los roles asignados
        rutas = []

        if rol in ["ADMIN", "RECEPCIONISTA (ventas)"]:
            rutas.append(("recepcion", "📋", "Recepción y Asignación de Tareas", ViewRecepcion))
            rutas.append(("finanzas", "💳", "Control de Pagos y Facturación", ViewFinanzas))

        if rol in ["ADMIN", "MECANICO"]:
            rutas.append(("mecanico", "🔧", "Taller y Órdenes de Mecánico", ViewMecanico))

        if rol == "ADMIN":
            rutas.append(("reportes", "📊", "Matriz Analítica de Rendimiento", ViewReportes))
            rutas.append(("usuarios", "👥", "Gestión de Operadores y Roles", RegistroUsuarioView))
        #botones de navegación
        for clave, icono, titulo, vista_cls in rutas:
            btn = ctk.CTkButton(
                sidebar,
                text=icono,
                width=48,
                height=48,
                corner_radius=14,
                fg_color="transparent",
                hover_color=BG_CARD,
                font=ctk.CTkFont(size=20),
                command=lambda c=clave, t=titulo, v=vista_cls: self.cambiar_vista(c, t, v)
            )
            btn.pack(pady=7)
            self.botones_nav[clave] = btn

        #Seleccionar la vista inicial
        if rutas:
            primer_clave, _, primer_titulo, primer_vista = rutas[0]
            self.cambiar_vista(primer_clave, primer_titulo, primer_vista)

    def cambiar_vista(self, clave_seleccionada, titulo_vista, VistaClase):
        """Intercambia la vista en el área central y resalta el botón activo."""
        #Limpiar área de contenido
        for widget in self.content_area.winfo_children():
            widget.destroy()
        #Actualizar título en el navbar
        self.lbl_modulo_actual.configure(text=titulo_vista.upper())
        #Actualizar estilo en el sidebar
        for clave, btn in self.botones_nav.items():
            if clave == clave_seleccionada:
                btn.configure(
                    fg_color=BG_CARD,
                    text_color=ACCENT_CYAN,
                    border_width=1,
                    border_color=ACCENT_CYAN
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=TEXT_MUTED,
                    border_width=0
                )

        #Mostrar la pantalla solicitada
        self.vista_activa = VistaClase(self.content_area)
        self.vista_activa.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = TallerApp()
    app.mainloop()