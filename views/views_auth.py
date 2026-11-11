import customtkinter as ctk
from tkinter import messagebox
from core.auth import SesionManager, registrar_usuario, ROLES_VALIDOS


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success

        # Tarjeta central contenedora
        card = ctk.CTkFrame(self, width=420, corner_radius=14)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Títulos
        lbl_titulo = ctk.CTkLabel(
            card, 
            text="TALLER MOTOR", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        lbl_titulo.pack(padx=30, pady=(30, 4))

        lbl_sub = ctk.CTkLabel(
            card, 
            text="Control de Acceso Basado en Roles (RBAC)", 
            text_color="gray70",
            font=ctk.CTkFont(size=12)
        )
        lbl_sub.pack(padx=30, pady=(0, 20))
        # Entradas de credenciales
        self.txt_user = ctk.CTkEntry(
            card, 
            placeholder_text="Nombre de usuario", 
            width=300, 
            height=42
        )
        self.txt_user.pack(padx=30, pady=10)

        self.txt_pass = ctk.CTkEntry(
            card, 
            placeholder_text="Contraseña", 
            show="*", 
            width=300, 
            height=42
        )
        self.txt_pass.pack(padx=30, pady=10)
        self.txt_pass.bind("<Return>", lambda event: self.ejecutar_login())

        # Botón de ingreso
        btn_ingresar = ctk.CTkButton(
            card, 
            text="Iniciar Sesión", 
            width=300, 
            height=42, 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.ejecutar_login
        )
        btn_ingresar.pack(padx=30, pady=(20, 20))
        # Cuadro de ayuda con credenciales de prueba
        lbl_demo = ctk.CTkLabel(
            card,
            text="Credenciales de prueba:\n"
                 "• Administrador: admin / admin123\n"
                 "• Recepción: recepcion / recep123\n"
                 "• Mecánico: mecanico1 / meca123",
            justify="left",
            text_color="gray60",
            font=ctk.CTkFont(size=11)
        )
        lbl_demo.pack(padx=30, pady=(0, 25))

    def ejecutar_login(self):
        """Valida que los campos no estén vacíos y comprueba el acceso."""
        usuario = self.txt_user.get().strip()
        password = self.txt_pass.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor complete ambos campos para ingresar.")
            return

        ok, msg = SesionManager.iniciar_sesion(usuario, password)
        if ok:
            self.on_login_success()
        else:
            messagebox.showerror("Error de Autenticación", msg)

class RegistroUsuarioView(ctk.CTkFrame):
    """
    Vista administrativa.
    """
    def __init__(self, master, on_success_callback=None):
        super().__init__(master, fg_color="transparent")
        self.on_success_callback = on_success_callback

        lbl_tit = ctk.CTkLabel(
            self, 
            text="Administración de Usuarios y Roles (RBAC)", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 10))

        box = ctk.CTkFrame(self)
        box.pack(fill="x", padx=20, pady=10)

        self.ent_user = ctk.CTkEntry(box, placeholder_text="Nombre de usuario", width=220)
        self.ent_user.grid(row=0, column=0, padx=10, pady=12)

        self.ent_pass = ctk.CTkEntry(box, placeholder_text="Contraseña", show="*", width=220)
        self.ent_pass.grid(row=0, column=1, padx=10, pady=12)

        self.cmb_rol = ctk.CTkComboBox(box, values=ROLES_VALIDOS, width=220)
        self.cmb_rol.grid(row=0, column=2, padx=10, pady=12)
        if ROLES_VALIDOS:
            self.cmb_rol.set(ROLES_VALIDOS[0])

        btn_crear = ctk.CTkButton(
            box, 
            text="Registrar Usuario", 
            fg_color="#2b7a4b", 
            hover_color="#1e5835",
            command=self.guardar_usuario
        )
        btn_crear.grid(row=0, column=3, padx=10, pady=12)

    def guardar_usuario(self):
        """Valida el nuevo usuario en el sistema."""
        u = self.ent_user.get().strip() #usuario
        p = self.ent_pass.get().strip() #contraseña
        r = self.cmb_rol.get().strip() #rol

        ok, msg = registrar_usuario(u, p, r)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.ent_user.delete(0, "end")
            self.ent_pass.delete(0, "end")
            if self.on_success_callback:
                self.on_success_callback()
        else:
            messagebox.showerror("Error de Registro", msg)
