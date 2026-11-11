import customtkinter as ctk
from tkinter import messagebox
from core.auth import SesionManager
from core.gestion_taller import listar_ordenes, transicionar_estado_orden

class ViewMecanico(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.cargar_ordenes()

    def cargar_ordenes(self):
        for widget in self.winfo_children():
            widget.destroy()

        lbl_tit = ctk.CTkLabel(self, text="Panel de Reparaciones Mecánicas", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))

        user_actual = SesionManager.usuario_actual["username"] if SesionManager.usuario_actual else ""
        rol = SesionManager.obtener_rol()

        lbl_sub = ctk.CTkLabel(self, text=f"Sesión activa: {user_actual} | Perfil: {rol}", text_color="gray70")
        lbl_sub.pack(anchor="w", padx=20, pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        todas = listar_ordenes()
        if rol == "MECANICO":
            ordenes = [o for o in todas if o.get("mecanico_asignado") == user_actual]
        else:
            ordenes = todas

        if not ordenes:
            ctk.CTkLabel(scroll, text="No hay órdenes asignadas o pendientes.", font=ctk.CTkFont(size=14)).pack(pady=40)
            return
        
        for o in ordenes:
            card = ctk.CTkFrame(scroll)
            card.pack(fill="x", padx=10, pady=8)

            estado = o.get("estado", "Pendiente")
            txt_info = (
                f"Orden #{o['id_orden']}  |  Fecha: {o['fecha']}  |  Mecánico: {o['mecanico_asignado']}\n"
                f"Vehículo: {o['marca_modelo_patente']}\n"
                f"Servicio / Tarea: {o['tipo_tarea']}  |  Monto Total: ${float(o['total']):,.2f}\n"
                f"Estado Actual: {estado}"
            )
            ctk.CTkLabel(card, text=txt_info, justify="left", font=ctk.CTkFont(size=12)).pack(side="left", padx=20, pady=12)

            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=20, pady=12)

            if estado == "Pendiente":
                btn_iniciar = ctk.CTkButton(btn_box, text="Iniciar Reparación", fg_color="#2980b9", hover_color="#1c5980", width=140,
                                            command=lambda oid=o["id_orden"]: self.cambiar_estado(oid, "En Reparacion"))
                btn_iniciar.pack(side="left", padx=5)
            elif estado == "En Reparacion":
                btn_finalizar = ctk.CTkButton(btn_box, text="Finalizar Tarea", fg_color="#27ae60", hover_color="#1e8449", width=140,
                                              command=lambda oid=o["id_orden"]: self.cambiar_estado(oid, "Finalizada"))
                btn_finalizar.pack(side="left", padx=5)
            elif estado in ["Finalizada", "Pagada"]:
                ctk.CTkLabel(btn_box, text="✓ Lista para cobro" if estado == "Finalizada" else "✓ Pagada", text_color="#2ecc71", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

        def cambiar_estado(self, id_orden, nuevo_estado):
            ok, msg = transicionar_estado_orden(id_orden, nuevo_estado)
            if ok:
                messagebox.showinfo("Estado Actualizado", msg)
                self.cargar_ordenes()
            else:
                messagebox.showerror("Error de Transición", msg)