"""
views_finanzas.py - Módulo de Finanzas: Presupuestos, Órdenes y Pagos
Implementa:
- Visualización tabular optimizada estilo Excel (ttk.Treeview).
- Resolución automática del cliente real mediante el vínculo de la patente con vehículos y clientes.
- Control de cobro, actualización dinámica de estados operativos y condición de pago.
"""
import customtkinter as ctk
from tkinter import ttk
from core.gestion_taller import listar_ordenes, transicionar_estado_orden, listar_vehiculos, listar_clientes

class ViewFinanzas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Configurar grid principal para ocupar toda la pantalla ordenadamente
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Título de la sección
        self.titulo = ctk.CTkLabel(
            self, 
            text="Finanzas: Presupuestos, Órdenes y Cobranzas", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.titulo.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 2))

        self.subtitulo = ctk.CTkLabel(
            self, 
            text="Gestión de cobro, visualización de clientes y actualización interactiva de estados (+ 15% IVA aplicado).",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.subtitulo.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        # Marco principal contenedor (Distribución 75% tabla / 25% panel de edición)
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

        # Columnas ajustadas para que entren perfectamente en la pantalla sin scroll horizontal
        self.columnas = ("id", "fecha", "cliente", "vehiculo", "tipo", "total", "estado", "pago")
        self.tree = ttk.Treeview(self.table_frame, columns=self.columnas, show="headings", selectmode="browse")

        # Configurar encabezados
        self.tree.heading("id", text="N°")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("vehiculo", text="Vehículo / Patente")
        self.tree.heading("tipo", text="Servicio")
        self.tree.heading("total", text="Total c/IVA")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("pago", text="Pago")

        # Anchos proporcionales calculados para el ancho estándar de pantalla
        self.tree.column("id", width=45, anchor="center")
        self.tree.column("fecha", width=80, anchor="center")
        self.tree.column("cliente", width=110, anchor="w")
        self.tree.column("vehiculo", width=140, anchor="w")
        self.tree.column("tipo", width=100, anchor="w")
        self.tree.column("total", width=85, anchor="e")
        self.tree.column("estado", width=95, anchor="center")
        self.tree.column("pago", width=95, anchor="center")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Evento de selección en la tabla
        self.tree.bind("<<TreeviewSelect>>", self.cargar_datos_en_panel_edicion)

        # --- PANEL LATERAL DE EDICIÓN RÁPIDA ---
        self.edit_panel = ctk.CTkFrame(self.main_container, fg_color="#242424", corner_radius=8)
        self.edit_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.edit_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.edit_panel, 
            text="Editar Orden", 
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(12, 5), sticky="w")

        self.lbl_seleccionada = ctk.CTkLabel(self.edit_panel, text="Seleccione una orden", text_color="gray70", font=("Arial", 10))
        self.lbl_seleccionada.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        # Selector de Estado Operativo
        ctk.CTkLabel(self.edit_panel, text="Estado Operativo:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=12, sticky="w")
        self.combo_estado = ctk.CTkComboBox(
            self.edit_panel, 
            values=["Pendiente", "En Reparacion", "Finalizada", "Pagada", "Cancelada"],
            state="readonly",
            width=190,
            height=28
        )
        self.combo_estado.grid(row=3, column=0, padx=12, pady=(3, 10), sticky="w")

        # Selector de Condición de Pago
        ctk.CTkLabel(self.edit_panel, text="Condición de Pago:", font=("Arial", 10, "bold")).grid(row=4, column=0, padx=12, sticky="w")
        self.combo_pago = ctk.CTkComboBox(
            self.edit_panel, 
            values=["Pendiente", "Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito"],
            state="readonly",
            width=190,
            height=28
        )
        self.combo_pago.grid(row=5, column=0, padx=12, pady=(3, 15), sticky="w")

        # Botón para Guardar Cambios
        self.btn_guardar = ctk.CTkButton(
            self.edit_panel, 
            text="Actualizar Orden", 
            fg_color="#1f538d", 
            hover_color="#143d6a",
            command=self.guardar_cambios_orden,
            width=190,
            height=30
        )
        self.btn_guardar.grid(row=6, column=0, padx=12, pady=5, sticky="w")

        # Mensaje de feedback
        self.lbl_feedback = ctk.CTkLabel(self.edit_panel, text="", text_color="lightgreen", font=("Arial", 10))
        self.lbl_feedback.grid(row=7, column=0, padx=12, pady=5, sticky="w")

        # Cargar datos iniciales
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Limpia y carga las órdenes resolviendo automáticamente el cliente real desde vehículos y clientes."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        ordenes = listar_ordenes()
        
        # Mapear vehículos y clientes para resolución automática
        vehiculos = listar_vehiculos()
        clientes_dict = {str(c['id_cliente']).strip(): c['nombre'] for c in listar_clientes()}
        vehiculo_a_cliente = {}
        for v in vehiculos:
            patente = v.get('patente', '').strip().upper()
            id_cli = str(v.get('id_cliente', '')).strip()
            if patente and id_cli:
                vehiculo_a_cliente[patente] = id_cli

        for o in ordenes:
            cliente_val = o.get('cliente', 'N/D')
            veh_info = o.get('marca_modelo_patente', '')

            # Si el cliente dice "Cliente Titular" o está vacío, intentamos buscar el nombre real por patente
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
                cliente_val,
                veh_info,
                o.get('tipo_tarea', 'General'),
                f"${float(o.get('total', 0)):,.2f}",
                o.get('estado', 'Pendiente'),
                o.get('metodo_pago', 'Pendiente')
            ))

    def cargar_datos_en_panel_edicion(self, event):
        """Rellena el panel lateral cuando el usuario selecciona una fila."""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion)
        valores = item.get("values")
        if valores:
            id_orden_limpio = valores[0].replace("#", "")
            self.lbl_seleccionada.configure(text=f"Orden #{id_orden_limpio} - {valores[2]}", text_color="white")
            self.combo_estado.set(valores[6])
            self.combo_pago.set(valores[7])
            self.lbl_feedback.configure(text="")

    def guardar_cambios_orden(self):
        """Aplica la modificación de estado y método de pago."""
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_feedback.configure(text="Seleccione una orden.", text_color="orange")
            return

        item = self.tree.item(seleccion)
        id_orden = item.get("values")[0].replace("#", "")
        nuevo_estado = self.combo_estado.get()
        nuevo_pago = self.combo_pago.get()

        exito, mensaje = transicionar_estado_orden(id_orden, nuevo_estado, nuevo_pago)
        if exito:
            self.lbl_feedback.configure(text="¡Actualizado!", text_color="lightgreen")
            self.actualizar_tabla()
        else:
            self.lbl_feedback.configure(text=mensaje, text_color="salmon")
