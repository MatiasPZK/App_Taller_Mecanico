"""
views_mecanico.py - Panel de Reparaciones Mecánicas
Implementa:
- Visualización tabular profesional estilo Excel (ttk.Treeview) con cabeceras e índice superior.
- Resolución automática del cliente real mediante el vínculo de la patente con vehículos y clientes.
- Filtrado inteligente según el rol (mecánicos ven solo sus tareas; administradores ven todo).
- Panel de control lateral para actualizar el estado operativo de forma dinámica.
"""
import customtkinter as ctk
from tkinter import ttk
from core.gestion_taller import listar_ordenes, transicionar_estado_orden, listar_vehiculos, listar_clientes
from core.auth import SesionManager

class ViewMecanico(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Obtener usuario actual para el filtro de rol (RBAC)
        self.usuario_actual = SesionManager.obtener_usuario_actual()
        self.rol = self.usuario_actual.get("rol", "INVITADO") if self.usuario_actual else "INVITADO"
        self.username = self.usuario_actual.get("username", "").strip().lower() if self.usuario_actual else ""

        # Título de la sección
        self.titulo = ctk.CTkLabel(
            self, 
            text="Panel de Reparaciones Mecánicas", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.titulo.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 2))

        sub_texto = "Bandeja operativa de taller y actualización de estados técnicos."
        if self.rol == "MECANICO":
            sub_texto += f" (Órdenes asignadas a: {self.usuario_actual.get('username')})"

        self.subtitulo = ctk.CTkLabel(
            self, 
            text=sub_texto,
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.subtitulo.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        # Marco principal contenedor (Distribución 75% tabla / 25% panel de control)
        self.main_container = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.main_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 15))
        self.main_container.grid_columnconfigure(0, weight=4)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # --- ÁREA DE LA TABLA ESTILO EXCEL (TREEVIEW) ---
        self.table_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Estilo profesional para ttk.Treeview en modo oscuro
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=26,
                        font=("Arial", 9))
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        font=("Arial", 9, "bold"))
        style.map("Treeview", background=[('selected', '#1f538d')])

        # Columnas de la tabla
        self.columnas = ("id", "fecha", "mecanico", "cliente", "vehiculo", "tipo", "estado")
        self.tree = ttk.Treeview(self.table_frame, columns=self.columnas, show="headings", selectmode="browse")

        # Configurar encabezados tipo índice de Excel
        self.tree.heading("id", text="N° Orden")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("mecanico", text="Mecánico")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("vehiculo", text="Vehículo / Patente")
        self.tree.heading("tipo", text="Servicio / Tarea")
        self.tree.heading("estado", text="ESTADO")

        # Anchos proporcionales para ajustar perfectamente en pantalla
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("fecha", width=85, anchor="center")
        self.tree.column("mecanico", width=95, anchor="center")
        self.tree.column("cliente", width=110, anchor="w")
        self.tree.column("vehiculo", width=140, anchor="w")
        self.tree.column("tipo", width=110, anchor="w")
        self.tree.column("estado", width=110, anchor="center")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_en_panel_edicion)

        # --- PANEL LATERAL DE GESTIÓN TÉCNICA ---
        self.edit_panel = ctk.CTkFrame(self.main_container, fg_color="#242424", corner_radius=8)
        self.edit_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.edit_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.edit_panel, 
            text="Control de Estado", 
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(12, 5), sticky="w")

        self.lbl_seleccionada = ctk.CTkLabel(self.edit_panel, text="Seleccione una orden", text_color="gray70", font=("Arial", 10))
        self.lbl_seleccionada.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        # Selector de Estado Operativo con botón/desplegable estilizado
        ctk.CTkLabel(self.edit_panel, text="Nuevo Estado:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=12, sticky="w")
        self.combo_estado = ctk.CTkComboBox(
            self.edit_panel, 
            values=["Pendiente", "En Reparacion", "Finalizada", "Cancelada"],
            state="readonly",
            width=190,
            height=28
        )
        self.combo_estado.grid(row=3, column=0, padx=12, pady=(3, 20), sticky="w")

        # Botón elegante para Aplicar Estado
        self.btn_guardar = ctk.CTkButton(
            self.edit_panel, 
            text="Actualizar Estado", 
            fg_color="#1f538d", 
            hover_color="#143d6a",
            command=self.guardar_cambios_orden,
            width=190,
            height=30
        )
        self.btn_guardar.grid(row=4, column=0, padx=12, pady=5, sticky="w")

        # Mensaje de feedback
        self.lbl_feedback = ctk.CTkLabel(self.edit_panel, text="", text_color="lightgreen", font=("Arial", 10))
        self.lbl_feedback.grid(row=5, column=0, padx=12, pady=5, sticky="w")

        # Cargar datos iniciales
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Limpia y carga las órdenes resolviendo automáticamente el cliente real y aplicando filtros de rol."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        ordenes = listar_ordenes()
        
        # Mapear vehículos y clientes para resolución automática del nombre real
        vehiculos = listar_vehiculos()
        clientes_dict = {str(c['id_cliente']).strip(): c['nombre'] for c in listar_clientes()}
        vehiculo_a_cliente = {}
        for v in vehiculos:
            patente = v.get('patente', '').strip().upper()
            id_cli = str(v.get('id_cliente', '')).strip()
            if patente and id_cli:
                vehiculo_a_cliente[patente] = id_cli

        for o in ordenes:
            mec_asignado = o.get('mecanico_asignado', '').strip()
            
            # Filtro RBAC visual para mecánicos
            if self.rol == "MECANICO" and mec_asignado.lower() != self.username:
                continue

            cliente_val = o.get('cliente', 'N/D')
            veh_info = o.get('marca_modelo_patente', '')

            # Resolución automática si dice "Cliente Titular" o está vacío
            if cliente_val in ["Cliente Titular", "", "N/D"]:
                veh_info_upper = veh_info.upper()
                for patente, id_cli in vehiculo_a_cliente.items():
                    if patente in veh_info_upper:
                        if id_cli in clientes_dict:
                            cliente_val = clientes_dict[id_cli]
                            break

            self.tree.insert("", "end", values=(
                f"#{o.get('id_orden')}",
                o.get('fecha'),
                mec_asignado if mec_asignado else "Sin Asignar",
                cliente_val,
                veh_info,
                o.get('tipo_tarea', 'General'),
                o.get('estado', 'Pendiente')
            ))

    def cargar_datos_en_panel_edicion(self, event):
        """Rellena el panel lateral al hacer clic en una orden."""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion)
        valores = item.get("values")
        if valores:
            id_orden_limpio = valores[0].replace("#", "")
            self.lbl_seleccionada.configure(text=f"Orden #{id_orden_limpio} - {valores[4]}", text_color="white")
            self.combo_estado.set(valores[6])
            self.lbl_feedback.configure(text="")

    def guardar_cambios_orden(self):
        """Aplica la transición de estado operativo."""
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_feedback.configure(text="Seleccione una orden.", text_color="orange")
            return

        item = self.tree.item(seleccion)
        id_orden = item.get("values")[0].replace("#", "")
        nuevo_estado = self.combo_estado.get()

        exito, mensaje = transicionar_estado_orden(id_orden, nuevo_estado)
        if exito:
            self.lbl_feedback.configure(text="¡Estado actualizado!", text_color="lightgreen")
            self.actualizar_tabla()
        else:
            self.lbl_feedback.configure(text=mensaje, text_color="salmon")
