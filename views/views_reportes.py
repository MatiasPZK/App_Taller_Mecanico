"""
views/views_reportes.py - Visualización de la Matriz Analítica de Rendimiento.
"""
import customtkinter as ctk
from tkinter import ttk
from core.reportes import generar_matriz_rendimiento

BG_CARD = "#14172f"
BORDER_COLOR = "#1f2448"
ACCENT_CYAN = "#00e5ff"
ACCENT_PINK = "#ff3366"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#7a82a6"


class ViewReportes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.construir_interfaz()

    def construir_interfaz(self):
        # 1. Cabecera con Título y Botón de Actualizar
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        lbl_tit = ctk.CTkLabel(
            header_frame,
            text="Rendimiento de Servicios por Mecánico (Matriz Dinámica)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_WHITE
        )
        lbl_tit.pack(side="left")

        btn_actualizar = ctk.CTkButton(
            header_frame,
            text="🔄 Actualizar Matriz",
            width=140,
            height=32,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#14375e",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.cargar_datos
        )
        btn_actualizar.pack(side="right")

        # 2. Contenedor de Tarjetas de Métricas Rápidas
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 20))

        # 3. Contenedor principal de la tabla matricial
        self.table_container = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.table_container.pack(fill="both", expand=True)

        self.cargar_datos()

    def cargar_datos(self):
        # Obtener los datos calculados desde core/reportes.py
        datos = generar_matriz_rendimiento()
        categorias = datos.get("categorias", [])
        mecanicos = datos.get("mecanicos", [])
        matriz = datos.get("matriz", [])
        totales_filas = datos.get("totales_filas", [])
        totales_cols = datos.get("totales_columnas", [])
        gran_total = datos.get("gran_total", 0.0)

        # --- A. Limpiar y refrescar tarjetas superiores ---
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        self.crear_card(self.cards_frame, "FACTURACIÓN TOTAL", f"${gran_total:,.2f}", ACCENT_CYAN, 0)
        self.crear_card(self.cards_frame, "CATEGORÍAS ACTIVAS", str(len(categorias)), TEXT_WHITE, 1)
        self.crear_card(self.cards_frame, "MECÁNICOS ACTIVOS", str(len(mecanicos)), ACCENT_PINK, 2)

        # --- B. Limpiar y construir la tabla dinámica (Treeview) ---
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # Configuración de estilos ttk
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Matriz.Treeview",
            background=BG_CARD,
            foreground=TEXT_WHITE,
            fieldbackground=BG_CARD,
            rowheight=32,
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "Matriz.Treeview.Heading",
            background="#0e1126",
            foreground=ACCENT_CYAN,
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        estilo.map("Matriz.Treeview", background=[("selected", "#1b284f")])

        columnas = ["Categoria"] + mecanicos + ["Total_Categoria"]
        
        scroll_y = ctk.CTkScrollbar(self.table_container, orientation="vertical")
        scroll_x = ctk.CTkScrollbar(self.table_container, orientation="horizontal")

        tree = ttk.Treeview(
            self.table_container,
            columns=columnas,
            show="headings",
            style="Matriz.Treeview",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        scroll_y.configure(command=tree.yview)
        scroll_x.configure(command=tree.xview)

        # Encabezados
        tree.heading("Categoria", text="Categoría / Servicio")
        tree.column("Categoria", width=180, anchor="w")

        for mec in mecanicos:
            tree.heading(mec, text=f"🔧 {mec}")
            tree.column(mec, width=130, anchor="center")

        tree.heading("Total_Categoria", text="Total Rubro")
        tree.column("Total_Categoria", width=140, anchor="e")

        # Cargar filas por categoría
        for i, cat in enumerate(categorias):
            valores_fila = [cat]
            for j in range(len(mecanicos)):
                monto_celda = matriz[i][j]
                valores_fila.append(f"${monto_celda:,.2f}" if monto_celda > 0 else "-")
            valores_fila.append(f"${totales_filas[i]:,.2f}")
            tree.insert("", "end", values=valores_fila)

        # Fila de Totales por Mecánico (Pie de matriz)
        fila_totales = ["TOTALES GENERALES"]
        for tot_col in totales_cols:
            fila_totales.append(f"${tot_col:,.2f}")
        fila_totales.append(f"${gran_total:,.2f}")
        tree.insert("", "end", values=fila_totales)

        # Empaquetado de la tabla y scrollbars
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def crear_card(self, parent, titulo, valor, color_acento, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.pack(side="left", fill="x", expand=True, padx=(0 if col == 0 else 10, 0))

        lbl_t = ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_t.pack(anchor="w", padx=16, pady=(12, 2))

        lbl_v = ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color_acento
        )
        lbl_v.pack(anchor="w", padx=16, pady=(0, 12))