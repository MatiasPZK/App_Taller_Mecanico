"""
views_finanzas.py - Módulo de Finanzas: Presupuestos, Órdenes y Pagos
Implementa:
- Visualización de montos con recargo de 15% IVA.
- Control de cobro (Efectivo / Transferencia).
- Emisión lógica de comprobante de pago.
"""
import customtkinter as ctk
from tkinter import messagebox
from core.gestor_taller import listar_ordenes, transicionar_estado_orden

class ViewFinanzas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.construir_interfaz()

    def construir_interfaz(self):
        for widget in self.winfo_children():
            widget.destroy()

        lbl_tit = ctk.CTkLabel(self, text="Finanzas: Presupuestos, Órdenes y Cobranzas", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))

        lbl_desc = ctk.CTkLabel(self, text="Gestión de cobro y emisión de comprobantes (+ 15% IVA aplicado según normativa del taller)", text_color="gray70")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        ordenes = listar_ordenes()
        if not ordenes:
            ctk.CTkLabel(scroll, text="No hay registros financieros ni órdenes emitidas.", font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        for o in ordenes:
            card = ctk.CTkFrame(scroll)
            card.pack(fill="x", padx=10, pady=8)

            txt = (
                f"Orden #{o['id_orden']}  |  Fecha: {o['fecha']}  |  Vehículo: {o['marca_modelo_patente']}\n"
                f"Servicio: {o['tipo_tarea']}  |  Monto Total c/15% IVA: ${float(o['total']):,.2f}\n"
                f"Estado Operativo: {o['estado']}  |  Condición de Pago: {o['metodo_pago']}"
            )
            ctk.CTkLabel(card, text=txt, justify="left", font=ctk.CTkFont(size=12)).pack(side="left", padx=20, pady=12)

            acciones = ctk.CTkFrame(card, fg_color="transparent")
            acciones.pack(side="right", padx=20, pady=12)

            if o["estado"] == "Finalizada" and o["metodo_pago"] == "Pendiente":
                btn_cobro = ctk.CTkButton(
                    acciones,
                    text="Cobrar y Emitir Comprobante",
                    fg_color="#2b7a4b",
                    hover_color="#1e5835",
                    width=210,
                    height=36,
                    command=lambda oid=o["id_orden"], m=o["total"]: self.registrar_cobranza(oid, m)
                )
                btn_cobro.pack(side="left", padx=5)
            elif o["estado"] == "Pagada":
                ctk.CTkLabel(acciones, text="[COBRADO - COMPROBANTE EMITIDO]", text_color="#27ae60", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            else:
                ctk.CTkLabel(acciones, text=f"[En Proceso: {o['estado']}]", text_color="gray60").pack(side="left", padx=10)

    def registrar_cobranza(self, id_orden, monto):
        ok, msg = transicionar_estado_orden(id_orden, "Pagada", metodo_pago="Efectivo / Transferencia")
        if ok:
            messagebox.showinfo("Comprobante Emitido", f"¡Pago registrado exitosamente para la Orden #{id_orden}!\nMonto liquidado con 15% IVA: ${float(monto):,.2f}\nComprobante de cobro emitido y archivado.")
            self.construir_interfaz()
        else:
            messagebox.showerror("Error de Cobro", msg)