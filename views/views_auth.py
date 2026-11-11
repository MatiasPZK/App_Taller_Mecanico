import customtkinter as ctk
from tkinter import messagebox, ttk
from core.auth import (
    SesionManager, 
    registrar_usuario, 
    ROLES_VALIDOS,
    obtener_todos_usuarios,
    dar_baja_usuario
)


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
    Vista administrativa para alta, listado y baja de operadores.
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

        # Panel de creación
        box = ctk.CTkFrame(self)
        box.pack(fill="x", padx=20, pady=(0, 15))

        self.ent_user = ctk.CTkEntry(box, placeholder_text="Nombre de usuario", width=200)
        self.ent_user.grid(row=0, column=0, padx=10, pady=12)

        self.ent_pass = ctk.CTkEntry(box, placeholder_text="Contraseña", show="*", width=200)
        self.ent_pass.grid(row=0, column=1, padx=10, pady=12)

        self.cmb_rol = ctk.CTkComboBox(box, values=ROLES_VALIDOS, width=210)
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

        # Barra de acciones de la tabla
        bar_acciones = ctk.CTkFrame(self, fg_color="transparent")
        bar_acciones.pack(fill="x", padx=20, pady=(0, 5))

        lbl_subtit = ctk.CTkLabel(
            bar_acciones, 
            text="Operadores Registrados", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_subtit.pack(side="left")

        btn_eliminar = ctk.CTkButton(
            bar_acciones,
            text="Dar de Baja Seleccionado",
            fg_color="#912d2d",
            hover_color="#6e2020",
            command=self.eliminar_usuario_seleccionado
        )
        btn_eliminar.pack(side="right")

        # Configuración estética oscura para Treeview
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#14172f",
            foreground="#ffffff",
            fieldbackground="#14172f",
            rowheight=28,
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "Treeview.Heading",
            background="#0e1126",
            foreground="#00e5ff",
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        estilo.map("Treeview", background=[("selected", "#1f538d")])

        # Contenedor de la tabla
        self.frame_lista_usuarios = ctk.CTkFrame(self)
        self.frame_lista_usuarios.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.scroll_y = ctk.CTkScrollbar(self.frame_lista_usuarios, orientation="vertical")
        self.scroll_x = ctk.CTkScrollbar(self.frame_lista_usuarios, orientation="horizontal")  

        self.tree = ttk.Treeview(
            self.frame_lista_usuarios, 
            columns=("ID", "Usuario", "Rol", "Activo"), 
            show="headings", 
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )
        self.scroll_y.configure(command=self.tree.yview)
        self.scroll_x.configure(command=self.tree.xview)

        # Configuración de columnas y encabezados
        self.tree.heading("ID", text="ID")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Rol", text="Rol Asignado")
        self.tree.heading("Activo", text="Estado")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Usuario", width=220, anchor="w")
        self.tree.column("Rol", width=220, anchor="w")
        self.tree.column("Activo", width=120, anchor="center")

        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Cargar los datos al iniciar
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Lee usuarios del archivo CSV y recarga las filas de la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = obtener_todos_usuarios()
        for u in usuarios:
            id_u = u.get("id_usuario", "")
            username = u.get("username", "")
            rol = u.get("rol", "")
            es_activo = str(u.get("activo", "true")).lower()
            estado = "Activo" if es_activo == "true" else "Inactivo"

            self.tree.insert("", "end", values=(id_u, username, rol, estado))

    def guardar_usuario(self):
        """Valida y registra el nuevo usuario en el sistema."""
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        r = self.cmb_rol.get().strip()

        ok, msg = registrar_usuario(u, p, r)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.ent_user.delete(0, "end")
            self.ent_pass.delete(0, "end")
            self.cargar_usuarios()
            if self.on_success_callback:
                self.on_success_callback()
        else:
            messagebox.showerror("Error de Registro", msg)

    def eliminar_usuario_seleccionado(self):
        """Aplica la baja lógica al usuario seleccionado en la tabla."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un usuario de la lista para dar de baja.")
            return

        item = self.tree.item(seleccion[0])
        valores = item["values"]
        id_usuario = str(valores[0])
        username = str(valores[1])
        rol = str(valores[2])

        # Validaciones de seguridad
        usuario_en_sesion = SesionManager.obtener_usuario_actual() or {}
        if usuario_en_sesion.get("username") == username:
            messagebox.showerror("Operación Denegada", "No puede dar de baja su propio usuario mientras tiene la sesión activa.")
            return

        if rol == "ADMIN":
            messagebox.showerror("Operación Denegada", "Los usuarios con rol ADMIN no pueden ser dados de baja.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Baja", 
            f"¿Está seguro de que desea dar de baja al usuario '{username}' (ID #{id_usuario})?"
        )
        if not confirmar:
            return

        ok, msg = dar_baja_usuario(id_usuario)
        if ok:
            messagebox.showinfo("Baja Exitosa", msg)
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", msg)