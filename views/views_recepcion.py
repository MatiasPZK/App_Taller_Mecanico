"""
views_recepcion.py - Módulo de Recepción y Asignación de Tareas
Cumple con el diagrama del sistema:
- Alta de Clientes y Vehículos asociados.
- Asignación de Tareas mediante menús desplegables enlazados.
- Catálogo de Servicios con IVA (15%).
- Creación de Órdenes de Trabajo en estado 'Pendiente'.
"""
import customtkinter as ctk
from tkinter import messagebox
from core.gestion_taller import (
    listar_clientes, registrar_cliente,
    listar_vehiculos, registrar_vehiculo,
    listar_servicios, registrar_servicio,
    crear_orden
)
from core.auth import obtener_todos_usuarios


class ViewRecepcion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.construir_interfaz()

    def construir_interfaz(self):
        lbl_titulo = ctk.CTkLabel(
            self, 
            text="Módulo de Recepción, Vehículos y Tareas", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(anchor="w", padx=20, pady=(15, 10))

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        tab_registro = tabview.add("1. Clientes y Vehículos")
        tab_asignar = tabview.add("2. Asignar Tarea / Orden")
        tab_servicios = tabview.add("3. Catálogo de Servicios")

        # PESTAÑA 1: CLIENTES Y VEHÍCULOS
        frame_cv = ctk.CTkScrollableFrame(tab_registro)
        frame_cv.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_c_tit = ctk.CTkLabel(frame_cv, text="Registro de Cliente", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_c_tit.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        self.txt_nom = ctk.CTkEntry(frame_cv, placeholder_text="Nombre y Apellido", width=260)
        self.txt_nom.grid(row=1, column=0, padx=10, pady=6)

        self.txt_dir = ctk.CTkEntry(frame_cv, placeholder_text="Dirección / Casa", width=260)
        self.txt_dir.grid(row=1, column=1, padx=10, pady=6)

        self.txt_cont = ctk.CTkEntry(frame_cv, placeholder_text="Número de Teléfono / Email", width=260)
        self.txt_cont.grid(row=2, column=0, padx=10, pady=6)

        lbl_v_tit = ctk.CTkLabel(frame_cv, text="Vehículo Asociado", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_v_tit.grid(row=3, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")

        self.txt_tipo = ctk.CTkEntry(frame_cv, placeholder_text="Tipo (Sedán, Pickup, SUV, Hatchback)", width=260)
        self.txt_tipo.grid(row=4, column=0, padx=10, pady=6)

        self.txt_marca = ctk.CTkEntry(frame_cv, placeholder_text="Marca (ej. Toyota, Ford)", width=260)
        self.txt_marca.grid(row=4, column=1, padx=10, pady=6)

        self.txt_mod_anio = ctk.CTkEntry(frame_cv, placeholder_text="Modelo y Año (ej. Yaris 2023)", width=260)
        self.txt_mod_anio.grid(row=5, column=0, padx=10, pady=6)

        self.txt_patente = ctk.CTkEntry(frame_cv, placeholder_text="Patente / Matrícula (ej. AB123CD)", width=260)
        self.txt_patente.grid(row=5, column=1, padx=10, pady=6)

        btn_guardar = ctk.CTkButton(
            frame_cv, 
            text="Guardar Cliente y Vehículo", 
            fg_color="#2b7a4b", 
            hover_color="#1e5835", 
            height=38, 
            command=self.guardar_cliente_vehiculo
        )
        btn_guardar.grid(row=6, column=0, columnspan=2, padx=10, pady=(20, 15), sticky="ew")

        # PESTAÑA 2: ASIGNACIÓN DE TAREAS
        frame_t = ctk.CTkScrollableFrame(tab_asignar)
        frame_t.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_t_desc = ctk.CTkLabel(frame_t, text="Generación de Órdenes de Reparación", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_t_desc.pack(anchor="w", padx=15, pady=(5, 10))

        lbl_dv = ctk.CTkLabel(frame_t, text="Seleccionar Vehículo Registrado (Menú Desplegable):", font=ctk.CTkFont(weight="bold"))
        lbl_dv.pack(anchor="w", padx=15, pady=(5, 2))
        self.cmb_veh = ctk.CTkComboBox(frame_t, width=480, height=36)
        self.cmb_veh.pack(anchor="w", padx=15, pady=(0, 10))

        lbl_ds = ctk.CTkLabel(frame_t, text="Seleccionar Servicio Preestablecido (con 15% IVA):", font=ctk.CTkFont(weight="bold"))
        lbl_ds.pack(anchor="w", padx=15, pady=(5, 2))
        self.cmb_serv = ctk.CTkComboBox(frame_t, width=480, height=36)
        self.cmb_serv.pack(anchor="w", padx=15, pady=(0, 10))

        lbl_dm = ctk.CTkLabel(frame_t, text="Mecánico Asignado:", font=ctk.CTkFont(weight="bold"))
        lbl_dm.pack(anchor="w", padx=15, pady=(5, 2))
        self.cmb_mec = ctk.CTkComboBox(frame_t, width=480, height=36)
        self.cmb_mec.pack(anchor="w", padx=15, pady=(0, 15))

        btn_crear_orden = ctk.CTkButton(
            frame_t, 
            text="Crear Orden de Trabajo (Estado: Pendiente)", 
            fg_color="#1f538d", 
            hover_color="#163c66", 
            height=42, 
            command=self.crear_orden_trabajo
        )
        btn_crear_orden.pack(anchor="w", padx=15, pady=(10, 20))

        # PESTAÑA 3: SERVICIOS
        frame_s = ctk.CTkScrollableFrame(tab_servicios)
        frame_s.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_s_tit = ctk.CTkLabel(frame_s, text="Agregar Servicio al Catálogo", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_s_tit.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        self.txt_srv_cat = ctk.CTkEntry(frame_s, placeholder_text="Categoría (ej. Frenos, Motor, Mantenimiento)", width=240)
        self.txt_srv_cat.grid(row=1, column=0, padx=10, pady=6)

        self.txt_srv_det = ctk.CTkEntry(frame_s, placeholder_text="Detalles del trabajo", width=280)
        self.txt_srv_det.grid(row=1, column=1, padx=10, pady=6)

        self.txt_srv_pre = ctk.CTkEntry(frame_s, placeholder_text="Precio Base ($)", width=180)
        self.txt_srv_pre.grid(row=2, column=0, padx=10, pady=6)

        btn_crear_srv = ctk.CTkButton(
            frame_s, 
            text="Registrar Servicio (+15% IVA)", 
            fg_color="#2b7a4b", 
            command=self.guardar_nuevo_servicio
        )
        btn_crear_srv.grid(row=2, column=1, padx=10, pady=6, sticky="ew")

        self.actualizar_combos()

    def actualizar_combos(self):
        vehiculos = listar_vehiculos()
        servicios = listar_servicios()
        usuarios = obtener_todos_usuarios()

        opciones_v = [f"{v['patente']} - {v['marca']} {v['modelo_anio']}" for v in vehiculos] or ["Sin vehículos disponibles"]
        opciones_s = [f"{s['categoria']} - {s['detalles']} (${float(s.get('total_iva', s.get('total_con_iva', 0))):,.2f} c/IVA)" for s in servicios] or ["Sin servicios disponibles"]
        mecanicos = [u["username"] for u in usuarios if u.get("rol") == "MECANICO" and str(u.get("activo", "true")).lower() == "true"] or ["Sin mecánicos activos"]

        self.cmb_veh.configure(values=opciones_v)
        self.cmb_veh.set(opciones_v[0])

        self.cmb_serv.configure(values=opciones_s)
        self.cmb_serv.set(opciones_s[0])

        self.cmb_mec.configure(values=mecanicos)
        self.cmb_mec.set(mecanicos[0])

    def guardar_cliente_vehiculo(self):
        ok_c, res_c = registrar_cliente(self.txt_nom.get(), self.txt_dir.get(), self.txt_cont.get())
        if not ok_c:
            messagebox.showerror("Error Cliente", res_c)
            return

        ok_v, res_v = registrar_vehiculo(res_c, self.txt_tipo.get(), self.txt_marca.get(), self.txt_mod_anio.get(), self.txt_patente.get())
        if not ok_v:
            messagebox.showerror("Error Vehículo", res_v)
            return

        messagebox.showinfo("Registro Exitoso", f"Cliente #{res_c} y Vehículo con Patente {self.txt_patente.get().upper()} guardados.")
        self.txt_nom.delete(0, "end")
        self.txt_dir.delete(0, "end")
        self.txt_cont.delete(0, "end")
        self.txt_tipo.delete(0, "end")
        self.txt_marca.delete(0, "end")
        self.txt_mod_anio.delete(0, "end")
        self.txt_patente.delete(0, "end")
        self.actualizar_combos()

    def crear_orden_trabajo(self):
        veh = self.cmb_veh.get()
        srv = self.cmb_serv.get()
        mec = self.cmb_mec.get()

        if "Sin vehículos" in veh or "Sin servicios" in srv or "Sin mecánicos" in srv:
            messagebox.showerror("Error", "Debe tener cargados vehículos, servicios y mecánicos para crear la orden.")
            return

        categoria = srv.split(" - ")[0]
        monto_total = 0.0
        for s in listar_servicios():
            if s.get("categoria") == categoria:
                monto_total = float(s.get("total_iva", s.get("total_con_iva", 0)))
                break

        ok, res_orden = crear_orden("Cliente Titular", veh, categoria, monto_total, mec)
        if ok:
            messagebox.showinfo("Orden Creada", f"Orden de trabajo #{res_orden} registrada en estado 'Pendiente'.\nTotal con 15% IVA: ${monto_total:,.2f}")
        else:
            messagebox.showerror("Error al Crear Orden", res_orden)

    def guardar_nuevo_servicio(self):
        cat = self.txt_srv_cat.get()
        det = self.txt_srv_det.get()
        pre = self.txt_srv_pre.get()

        try:
            p_float = float(pre)
            ok, msg = registrar_servicio(cat, det, p_float)
            if ok:
                messagebox.showinfo("Servicio Guardado", msg)
                self.txt_srv_cat.delete(0, "end")
                self.txt_srv_det.delete(0, "end")
                self.txt_srv_pre.delete(0, "end")
                self.actualizar_combos()
            else:
                messagebox.showerror("Error", msg)
        except ValueError:
            messagebox.showerror("Error", "El precio base debe ser un valor numérico.")