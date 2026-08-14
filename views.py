"""
Vistas de la aplicación usando CustomTkinter.
Cada vista es un frame independiente que se muestra en el panel central.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import csv
import webbrowser
import urllib.parse
from models import Categoria, Producto


class DashboardView(ctk.CTkFrame):
    """Vista del Dashboard con estadísticas generales"""
    
    def __init__(self, parent, categoria_service, producto_service, empresa_service=None, factura_service=None):
        super().__init__(parent, fg_color=("#F5F5F5", "#2b2b2b"))
        self.categoria_service = categoria_service
        self.producto_service = producto_service
        self.empresa_service = empresa_service
        self.factura_service = factura_service
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets del dashboard"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="Dashboard - Vista General",
            font=("Arial", 28, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        )
        title.pack(pady=30)
        
        # Frame para las tarjetas de estadísticas
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(pady=20, padx=40, fill="x")
        
        # Obtener estadísticas
        total_productos = self.producto_service.get_count()
        total_categorias = self.categoria_service.get_count()
        valor_inventario = self.producto_service.get_total_value()
        productos_bajo_stock = len(self.producto_service.get_low_stock(10))
        presupuesto = self.empresa_service.get_presupuesto() if self.empresa_service else 0.0
        
        # Estadísticas de ventas (Facturas)
        total_facturado = self.factura_service.get_total_facturas() if self.factura_service else 0.0
        conteo_facturas = self.factura_service.get_count() if self.factura_service else 0
        ventas_hoy = self.factura_service.get_total_ventas_hoy() if self.factura_service else 0.0
        
        # Tarjetas de estadísticas (2 filas, 3 columnas)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        # Primera fila
        self._create_stat_card(
            stats_frame,
            "💰 Presupuesto / Caja",
            f"${presupuesto:,.2f}",
            "#27ae60",
            0, 0
        )
        
        self._create_stat_card(
            stats_frame,
            "Total Productos",
            str(total_productos),
            "#3498db",
            0, 1
        )
        
        self._create_stat_card(
            stats_frame,
            "Categorías",
            str(total_categorias),
            "#2D5A27",
            0, 2
        )
        
        # Segunda fila
        self._create_stat_card(
            stats_frame,
            "Valor Inventario",
            f"${valor_inventario:,.2f}",
            "#9b59b6",
            1, 0
        )
        
        self._create_stat_card(
            stats_frame,
            "Ventas Totales",
            f"${total_facturado:,.2f}",
            "#e67e22",
            1, 1
        )
        
        self._create_stat_card(
            stats_frame,
            "Ventas de Hoy",
            f"${ventas_hoy:,.2f}",
            "#27ae60",
            1, 2
        )
        
        # Productos con stock bajo
        productos_bajo_stock = self.producto_service.get_low_stock(5)
        if productos_bajo_stock:
            self._create_low_stock_section(productos_bajo_stock)
    
    def _create_stat_card(self, parent, title, value, color, row, col):
        """Crea una tarjeta de estadística"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1) # Ensure equal width
        parent.grid_rowconfigure(row, weight=1) # Ensure equal height
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14),
            text_color="white"
        )
        title_label.pack(pady=(20, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        value_label.pack(pady=(5, 20))
    
    def _create_low_stock_section(self, productos):
        """Crea la sección de alerta de stock bajo"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=20, padx=40, fill="x")
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="#c0392b", corner_radius=5)
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            header,
            text=f"⚠️ ALERTA: {len(productos)} Productos con Stock Crítico (Menos de 5)",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Lista
        scroll_frame = ctk.CTkScrollableFrame(frame, height=200, fg_color=("white", "#333333"))
        scroll_frame.pack(fill="x")
        
        for p in productos:
            p_frame = ctk.CTkFrame(scroll_frame, fg_color=("#F5F5F5", "#2b2b2b"))
            p_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                p_frame, 
                text=f"{p.nombre}", 
                font=("Arial", 12, "bold"),
                anchor="w",
                width=200,
                text_color=("black", "white")
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                p_frame, 
                text=f"Stock: {p.stock}", 
                text_color="#e74c3c",
                font=("Arial", 12, "bold"),
                anchor="w"
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                p_frame,
                text="Ordenar",
                width=80,
                height=25,
                fg_color="#e67e22",
                command=lambda prod=p: self.open_order_dialog(prod)
            ).pack(side="right", padx=10)
    
    def open_order_dialog(self, producto):
        """Abre diálogo para pedir a proveedor"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Reponer {producto.nombre}")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"Reponer: {producto.nombre}", font=("Arial", 14, "bold")).pack(pady=10)
        
        cant_entry = ctk.CTkEntry(dialog, placeholder_text="Cantidad a pedir")
        cant_entry.pack(pady=10)
        
        def enviar():
            try:
                cantidad = int(cant_entry.get())
                self.send_whatsapp(producto, cantidad)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese número válido")
                
        ctk.CTkButton(dialog, text="📲 Enviar a WhatsApp", fg_color="#27ae60", command=enviar).pack(pady=10)

    def send_whatsapp(self, producto, cantidad):
        """Abre WhatsApp Web con mensaje"""
        mensaje = f"Hola, necesito pedir {cantidad} unidades de {producto.nombre}. ¿Me confirmas stock?"
        encoded_msg = urllib.parse.quote(mensaje)
        url = f"https://wa.me/?text={encoded_msg}"
        webbrowser.open(url)

    
    def refresh(self):
        """Refresca la vista del dashboard"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()


class ProductosView(ctk.CTkFrame):
    """Vista de gestión de productos"""
    
    def __init__(self, parent, categoria_service, producto_service):
        super().__init__(parent, fg_color=("#F5F5F5", "#2b2b2b"))
        self.categoria_service = categoria_service
        self.producto_service = producto_service
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets de la vista de productos"""
        # Título y barra de búsqueda
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=40, fill="x")
        
        title = ctk.CTkLabel(
            header_frame,
            text="📦 Gestión de Productos",
            font=("Arial", 28, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        )
        title.pack(side="left")
        
        # Botón Agregar
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Producto",
            font=("Arial", 14, "bold"),
            fg_color="#FF6B35",
            hover_color="#E55A25",
            command=self.add_producto
        )
        add_btn.pack(side="right", padx=10)
        
        # Botón Exportar
        export_btn = ctk.CTkButton(
            header_frame,
            text="📥 Exportar Excel",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.export_to_csv
        )
        export_btn.pack(side="right", padx=10)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=10, padx=40, fill="x")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar producto...",
            font=("Arial", 14),
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Buscar",
            font=("Arial", 14),
            fg_color="#2D5A27",
            hover_color="#1F4019",
            width=100,
            command=self.search_productos
        )
        search_btn.pack(side="left")
        
        # Frame con scroll para la tabla
        self.table_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("white", "#333333"),
            corner_radius=15
        )
        self.table_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        self.load_productos()
    
    def load_productos(self, productos=None):
        """Carga los productos en la tabla"""
        # Limpiar tabla
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Encabezados
        headers = ["Nombre", "Categoría", "Precio", "Stock", "Acciones"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="#2D5A27")
        header_frame.pack(fill="x", pady=(0, 10))
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="white"
            )
            label.grid(row=0, column=i, padx=20, pady=15, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1) # Make columns fill space
        
        # Obtener productos
        if productos is None:
            productos = self.producto_service.get_all()
        
        # Filas de datos
        for idx, producto in enumerate(productos):
            # Adaptive colors: (Light Mode, Dark Mode)
            bg_color = ("#F5F5F5", "#2b2b2b") if idx % 2 == 0 else ("white", "#333333")
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color)
            row_frame.pack(fill="x", pady=2)
            
            # Highlight if low stock (critical)
            is_critical = producto.stock < 5
            
            # Nombre
            ctk.CTkLabel(
                row_frame,
                text=producto.nombre,
                font=("Arial", 12),
                anchor="w",
                text_color=("black", "white")
            ).grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
            
            # Categoría
            categoria_nombre = getattr(producto, 'categoria_nombre', 'Sin categoría')
            ctk.CTkLabel(
                row_frame,
                text=categoria_nombre,
                font=("Arial", 12),
                anchor="w",
                text_color=("black", "white")
            ).grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
            
            # Precio
            ctk.CTkLabel(
                row_frame,
                text=f"${producto.precio:.2f}",
                font=("Arial", 12),
                anchor="w",
                text_color=("black", "white")
            ).grid(row=0, column=2, padx=20, pady=10, sticky="nsew")
            
            # Stock
            stock_color = "#e74c3c" if is_critical else ("#FF6B35" if producto.stock <= 10 else "#27ae60")
            stock_font = ("Arial", 12, "bold") if is_critical else ("Arial", 12)
            
            ctk.CTkLabel(
                row_frame,
                text=str(producto.stock),
                font=stock_font,
                text_color=stock_color,
                anchor="w"
            ).grid(row=0, column=3, padx=20, pady=10, sticky="nsew")
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=4, padx=20, pady=5)
            
            # Configurar pesos de columnas
            for i in range(5):
                row_frame.grid_columnconfigure(i, weight=1)
            
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️ Editar",
                font=("Arial", 11),
                fg_color="#3498db",
                hover_color="#2980b9",
                width=80,
                command=lambda p=producto: self.edit_producto(p)
            )
            edit_btn.pack(side="left", padx=5)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                font=("Arial", 11),
                fg_color="#e74c3c",
                hover_color="#c0392b",
                width=40,
                command=lambda p=producto: self.delete_producto(p)
            )
            delete_btn.pack(side="left")
    
    def search_productos(self):
        """Busca productos"""
        search_term = self.search_entry.get().strip()
        if search_term:
            productos = self.producto_service.search(search_term)
            self.load_productos(productos)
        else:
            self.load_productos()
    
    def add_producto(self):
        """Abre diálogo para agregar producto"""
        dialog = ProductoDialog(self, self.categoria_service, self.producto_service)
        self.wait_window(dialog)
        self.load_productos()
    
    def edit_producto(self, producto):
        """Abre diálogo para editar producto"""
        dialog = ProductoDialog(
            self,
            self.categoria_service,
            self.producto_service,
            producto=producto
        )
        self.wait_window(dialog)
        self.load_productos()
    
    def delete_producto(self, producto):
        """Elimina un producto"""
        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar el producto '{producto.nombre}'?"
        ):
            self.producto_service.delete(producto.id)
            self.load_productos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    
    def refresh(self):
        """Refresca la vista"""
        self.load_productos()

    def export_to_csv(self):
        """Exporta el inventario a CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Exportar Inventario"
            )
            
            if filename:
                productos = self.producto_service.get_all()
                
                with open(filename, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter=';')
                    # Headers
                    writer.writerow(["ID", "Nombre", "Descripción", "Precio", "Stock", "Categoría"])
                    
                    # Data
                    for p in productos:
                        categoria = getattr(p, 'categoria_nombre', 'Sin categoría')
                        # Limpiar descripción de saltos de línea para no romper el CSV
                        desc = p.descripcion.replace('\n', ' ').replace('\r', '') if p.descripcion else ''
                        writer.writerow([p.id, p.nombre, desc, p.precio, p.stock, categoria])
                
                messagebox.showinfo("Éxito", "Inventario exportado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")


class CategoriasView(ctk.CTkFrame):
    """Vista de gestión de categorías con diseño de dos columnas"""
    
    def __init__(self, parent, categoria_service):
        super().__init__(parent, fg_color=("#F5F5F5", "#2b2b2b"))
        self.categoria_service = categoria_service
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets de la vista de categorías"""
        # Título
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=40, fill="x")
        
        title = ctk.CTkLabel(
            header_frame,
            text="🏷️ Gestión de Categorías",
            font=("Arial", 28, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        )
        title.pack(side="left")
        
        # Contenedor principal dividido en dos columnas
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(pady=10, padx=40, fill="both", expand=True)
        main_container.grid_columnconfigure(0, weight=3)  # Izquierda más ancha
        main_container.grid_columnconfigure(1, weight=2)  # Derecha más estrecha
        main_container.grid_rowconfigure(0, weight=1)
        
        # === COLUMNA IZQUIERDA: LISTA DE CATEGORÍAS ===
        left_frame = ctk.CTkFrame(main_container, fg_color=("white", "#333333"), corner_radius=15)
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(
            left_frame,
            text="Categorías Existentes",
            font=("Arial", 18, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        ).pack(pady=15)
        
        # Frame con scroll para la lista
        self.list_frame = ctk.CTkScrollableFrame(
            left_frame,
            fg_color=("#F5F5F5", "#2b2b2b")
        )
        self.list_frame.pack(pady=10, padx=15, fill="both", expand=True)
        
        # === COLUMNA DERECHA: FORMULARIO ===
        right_frame = ctk.CTkFrame(main_container, fg_color=("white", "#333333"), corner_radius=15)
        right_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        ctk.CTkLabel(
            right_frame,
            text="Nueva Categoría",
            font=("Arial", 18, "bold"),
            text_color="#2D5A27"
        ).pack(pady=15)
        
        # Formulario
        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Nombre
        ctk.CTkLabel(
            form_frame,
            text="Nombre:",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.nombre_entry = ctk.CTkEntry(
            form_frame,
            font=("Arial", 14),
            height=40,
            placeholder_text="Ej: Bebidas"
        )
        self.nombre_entry.pack(fill="x", pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(
            form_frame,
            text="Descripción (opcional):",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.desc_entry = ctk.CTkTextbox(
            form_frame,
            font=("Arial", 12),
            height=100
        )
        self.desc_entry.pack(fill="x", pady=(0, 20))
        
        # Botón Añadir
        add_btn = ctk.CTkButton(
            form_frame,
            text="➕ Añadir Categoría",
            font=("Arial", 16, "bold"),
            fg_color="#FF6B35",
            hover_color="#E55A25",
            height=50,
            command=self.add_categoria_from_form
        )
        add_btn.pack(fill="x", pady=10)
        
        # Cargar categorías
        self.load_categorias()
    
    def load_categorias(self):
        """Carga las categorías en la lista"""
        # Limpiar lista
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        categorias = self.categoria_service.get_all()
        
        if not categorias:
            ctk.CTkLabel(
                self.list_frame,
                text="No hay categorías creadas",
                font=("Arial", 12),
                text_color="gray"
            ).pack(pady=20)
            return
        
        for categoria in categorias:
            card = ctk.CTkFrame(
                self.list_frame,
                fg_color="white",
                corner_radius=10
            )
            card.pack(fill="x", pady=5, padx=10)
            
            # Contenido
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=12)
            
            # Nombre
            nombre_label = ctk.CTkLabel(
                content_frame,
                text=categoria.nombre,
                font=("Arial", 15, "bold"),
                text_color=("#2D5A27", "#2ecc71"),
                anchor="w"
            )
            nombre_label.pack(side="left", fill="x", expand=True)
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            actions_frame.pack(side="right")
            
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                font=("Arial", 12),
                fg_color="#3498db",
                hover_color="#2980b9",
                width=40,
                command=lambda c=categoria: self.edit_categoria(c)
            )
            edit_btn.pack(side="left", padx=3)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                font=("Arial", 12),
                fg_color="#e74c3c",
                hover_color="#c0392b",
                width=40,
                command=lambda c=categoria: self.delete_categoria(c)
            )
            delete_btn.pack(side="left", padx=3)
            
            # Descripción
            if categoria.descripcion:
                desc_label = ctk.CTkLabel(
                    card,
                    text=categoria.descripcion,
                    font=("Arial", 11),
                    text_color="gray",
                    anchor="w"
                )
                desc_label.pack(padx=15, pady=(0, 10), fill="x")
    
    def add_categoria_from_form(self):
        """Añade categoría desde el formulario integrado"""
        nombre = self.nombre_entry.get().strip()
        descripcion = self.desc_entry.get("1.0", "end-1c").strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            from models import Categoria
            nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)
            self.categoria_service.create(nueva_categoria)
            
            # Limpiar formulario
            self.nombre_entry.delete(0, 'end')
            self.desc_entry.delete("1.0", "end")
            
            # Actualizar lista
            self.load_categorias()
            
            messagebox.showinfo("Éxito", f"Categoría '{nombre}' creada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear categoría: {str(e)}")
    
    def edit_categoria(self, categoria):
        """Abre diálogo para editar categoría"""
        dialog = CategoriaDialog(self, self.categoria_service, categoria=categoria)
        self.wait_window(dialog)
        self.load_categorias()
    
    def delete_categoria(self, categoria):
        """Elimina una categoría"""
        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la categoría '{categoria.nombre}'?\n\n"
            "Los productos de esta categoría quedarán sin categoría."
        ):
            self.categoria_service.delete(categoria.id)
            self.load_categorias()
            messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
    
    def refresh(self):
        """Refresca la vista"""
        self.load_categorias()


class AjustesView(ctk.CTkFrame):
    """Vista de configuración y ajustes"""
    
    def __init__(self, parent, empresa_service=None, config_service=None):
        super().__init__(parent, fg_color=("#F5F5F5", "#2b2b2b"))
        self.parent = parent
        self.empresa_service = empresa_service
        self.config_service = config_service
        # Obtener referencia a la ventana principal
        self.main_window = self.winfo_toplevel()
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets de la vista de ajustes"""
        title = ctk.CTkLabel(
            self,
            text="⚙️ Configuración",
            font=("Arial", 28, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        )
        title.pack(pady=30)
        
        # Frame de configuraciones
        settings_frame = ctk.CTkFrame(self, fg_color=("white", "#333333"), corner_radius=15)
        settings_frame.pack(pady=20, padx=40, fill="both", expand=True)
        settings_frame.grid_columnconfigure(0, weight=1)  # Centrar contenido
        
        # Información de la aplicación
        info_section = ctk.CTkFrame(settings_frame, fg_color="transparent")
        info_section.pack(pady=30, padx=40, fill="x")
        
        ctk.CTkLabel(
            info_section,
            text="Aplicación de Distribuidora",
            font=("Arial", 20, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            info_section,
            text="Versión 1.0.0",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=2)
        
        ctk.CTkLabel(
            info_section,
            text="Desarrollado con Python y CustomTkinter",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(5, 20))
        
        
        # Gestión de Caja
        if self.empresa_service:
            caja_section = ctk.CTkFrame(settings_frame, fg_color=("#F5F5F5", "#2b2b2b"), corner_radius=10)
            caja_section.pack(pady=20, padx=40, fill="x")
            
            ctk.CTkLabel(
                caja_section,
                text="💰 Gestión de Caja",
                font=("Arial", 16, "bold"),
                text_color=("#2D5A27", "#2ecc71")
            ).pack(pady=15, padx=20, anchor="w")
            
            caja_content = ctk.CTkFrame(caja_section, fg_color="transparent")
            caja_content.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkLabel(
                caja_content,
                text="Saldo Actual:",
                font=("Arial", 14)
            ).pack(side="left", padx=(0, 10))
            
            self.presupuesto_label = ctk.CTkLabel(
                caja_content,
                text=f"${self.empresa_service.get_presupuesto():,.2f}",
                font=("Arial", 16, "bold"),
                text_color=("#27ae60", "#2ecc71")
            )
            self.presupuesto_label.pack(side="left", padx=(0, 20))
            
            self.nuevo_saldo_entry = ctk.CTkEntry(
                caja_content,
                placeholder_text="Nuevo Saldo",
                width=120
            )
            self.nuevo_saldo_entry.pack(side="left", padx=(0, 10))
            
            update_btn = ctk.CTkButton(
                caja_content,
                text="Actualizar Caja",
                fg_color="#e67e22",
                hover_color="#d35400",
                width=120,
                command=self.update_caja
            )
            update_btn.pack(side="left")
        
        # Opciones
        options_section = ctk.CTkFrame(settings_frame, fg_color=("#F5F5F5", "#2b2b2b"), corner_radius=10)
        options_section.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(
            options_section,
            text="Opciones de la Aplicación",
            font=("Arial", 16, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        ).pack(pady=15, padx=20, anchor="w")
        
        # Modo de Apariencia (Light/Dark/System)
        appearance_frame = ctk.CTkFrame(options_section, fg_color="transparent")
        appearance_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            appearance_frame,
            text="Modo de Apariencia:",
            font=("Arial", 14)
        ).pack(side="left", padx=(0, 20))
        
        # Load current mode
        current_mode = ctk.get_appearance_mode()
        appearance_var = ctk.StringVar(value=current_mode)
        
        appearance_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=["Light", "Dark", "System"],
            variable=appearance_var,
            font=("Arial", 12),
            fg_color="#2D5A27",
            button_color="#2D5A27",
            command=self.change_appearance_mode_event
        )
        appearance_menu.pack(side="left")
        
        # Tema de Color
        theme_frame = ctk.CTkFrame(options_section, fg_color="transparent")
        theme_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            theme_frame,
            text="Tema de Color:",
            font=("Arial", 14)
        ).pack(side="left", padx=(0, 20))
        
        self.theme_var = ctk.StringVar(value="Verde")
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Verde", "Azul", "Rojo"],
            variable=self.theme_var,
            font=("Arial", 12),
            fg_color="#2D5A27",
            button_color="#2D5A27",
            command=self.change_color_theme_event
        )
        theme_menu.pack(side="left")
        
        # Botón de información
        info_btn = ctk.CTkButton(
            settings_frame,
            text="ℹ️ Acerca de",
            font=("Arial", 14),
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.show_about
        )
        info_btn.pack(pady=20)
    
    def change_appearance_mode_event(self, new_appearance_mode):
        """Cambia el modo de apariencia entre Light, Dark y System"""
        ctk.set_appearance_mode(new_appearance_mode)
        # Save to persistence
        if self.config_service:
            self.config_service.set_config("modo", new_appearance_mode)

    
    def change_color_theme_event(self, new_theme):
        """Cambia el tema de color de los botones principales dinámicamente"""
        # Mapeo de temas a colores
        color_map = {
            "Verde": "#2D5A27",
            "Azul": "#1E3A8A",
            "Rojo": "#991B1B"
        }
        
        new_color = color_map.get(new_theme, "#2D5A27")
        
        # Intentar actualizar los botones de navegación en la ventana principal
        try:
            if hasattr(self.main_window, 'nav_buttons'):
                # Actualizar el color del sidebar
                if hasattr(self.main_window, 'sidebar'):
                    self.main_window.sidebar.configure(fg_color=new_color)
                
                # Actualizar el hover_color de los botones de navegación
                hover_colors = {
                    "Verde": "#1F4019",
                    "Azul": "#1E293B",
                    "Rojo": "#7F1D1D"
                }
                hover_color = hover_colors.get(new_theme, "#1F4019")
                
                for btn in self.main_window.nav_buttons:
                    btn.configure(hover_color=hover_color)
                    # Si el botón está activo, actualizar su color
                    if btn.cget("fg_color") != "transparent":
                        btn.configure(fg_color="#FF6B35")  # Mantener el color de acento
        except Exception as e:
            print(f"Error al cambiar tema: {e}")
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("Acerca de")
        about_window.geometry("400x350")
        about_window.resizable(False, False)
        about_window.transient(self) 
        about_window.grab_set()
        
        # Contenedor central
        container = ctk.CTkFrame(about_window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="🏢 Distribuidora App",
            font=("Arial", 22, "bold"),
            text_color="#2D5A27"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            container,
            text="Versión 1.0.0 Commercial",
            font=("Arial", 14, "bold"),
            text_color="gray"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            container,
            text="Sistema Integral de Gestión:\n\n• Inventario y Categorías\n• Facturación y Caja\n• Historial y Reportes",
            font=("Arial", 14),
            justify="center"
        ).pack(pady=20)
        
        ctk.CTkButton(
            container,
            text="Cerrar",
            command=about_window.destroy,
            width=120
        ).pack(side="bottom", pady=10)
    
    def update_caja(self):
        """Actualiza el saldo de caja"""
        try:
            nuevo_saldo = float(self.nuevo_saldo_entry.get())
            if nuevo_saldo < 0:
                messagebox.showerror("Error", "El saldo no puede ser negativo")
                return
                
            if messagebox.askyesno("Confirmar", f"¿Está seguro de establecer la caja en ${nuevo_saldo:,.2f}?"):
                self.empresa_service.establecer_presupuesto(nuevo_saldo)
                self.presupuesto_label.configure(text=f"${nuevo_saldo:,.2f}")
                self.nuevo_saldo_entry.delete(0, 'end')
                messagebox.showinfo("Éxito", "Caja actualizada correctamente")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")

    def refresh(self):
        """Refresca la vista"""
        if self.empresa_service:
            presupuesto = self.empresa_service.get_presupuesto()
            if hasattr(self, 'presupuesto_label'):
                self.presupuesto_label.configure(text=f"${presupuesto:,.2f}")


# --- Diálogos ---

class CategoriaDialog(ctk.CTkToplevel):
    """Diálogo para crear/editar categorías"""
    
    def __init__(self, parent, categoria_service, categoria=None):
        super().__init__(parent)
        self.categoria_service = categoria_service
        self.categoria = categoria
        
        self.title("Editar Categoría" if categoria else "Nueva Categoría")
        self.geometry("500x300")
        self.resizable(False, False)
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nombre
        ctk.CTkLabel(
            main_frame,
            text="Nombre:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.nombre_entry = ctk.CTkEntry(
            main_frame,
            font=("Arial", 14),
            height=40
        )
        self.nombre_entry.pack(fill="x", pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(
            main_frame,
            text="Descripción:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.desc_entry = ctk.CTkTextbox(
            main_frame,
            font=("Arial", 12),
            height=80
        )
        self.desc_entry.pack(fill="x", pady=(0, 15))
        
        # Cargar datos si es edición
        if self.categoria:
            self.nombre_entry.insert(0, self.categoria.nombre)
            self.desc_entry.insert("1.0", self.categoria.descripcion or "")
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            font=("Arial", 14, "bold"),
            fg_color="#2D5A27",
            hover_color="#1F4019",
            width=150,
            command=self.save
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=("Arial", 14),
            fg_color="gray",
            hover_color="#666",
            width=150,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=10)
    
    def save(self):
        """Guarda la categoría"""
        nombre = self.nombre_entry.get().strip()
        descripcion = self.desc_entry.get("1.0", "end-1c").strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            if self.categoria:
                # Editar
                self.categoria.nombre = nombre
                self.categoria.descripcion = descripcion
                self.categoria_service.update(self.categoria)
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
            else:
                # Crear
                nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)
                self.categoria_service.create(nueva_categoria)
                messagebox.showinfo("Éxito", "Categoría creada correctamente")
            
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class ProductoDialog(ctk.CTkToplevel):
    """Diálogo para crear/editar productos"""
    
    def __init__(self, parent, categoria_service, producto_service, producto=None):
        super().__init__(parent)
        self.categoria_service = categoria_service
        self.producto_service = producto_service
        self.producto = producto
        
        self.title("Editar Producto" if producto else "Nuevo Producto")
        self.geometry("550x500")
        self.resizable(False, False)
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nombre
        ctk.CTkLabel(
            main_frame,
            text="Nombre:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.nombre_entry = ctk.CTkEntry(
            main_frame,
            font=("Arial", 14),
            height=40
        )
        self.nombre_entry.pack(fill="x", pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(
            main_frame,
            text="Descripción:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.desc_entry = ctk.CTkTextbox(
            main_frame,
            font=("Arial", 12),
            height=80
        )
        self.desc_entry.pack(fill="x", pady=(0, 15))
        
        # Precio
        ctk.CTkLabel(
            main_frame,
            text="Precio:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.precio_entry = ctk.CTkEntry(
            main_frame,
            font=("Arial", 14),
            height=40,
            placeholder_text="0.00"
        )
        self.precio_entry.pack(fill="x", pady=(0, 15))
        
        # Stock
        ctk.CTkLabel(
            main_frame,
            text="Stock:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.stock_entry = ctk.CTkEntry(
            main_frame,
            font=("Arial", 14),
            height=40,
            placeholder_text="0"
        )
        self.stock_entry.pack(fill="x", pady=(0, 15))
        
        # Categoría
        ctk.CTkLabel(
            main_frame,
            text="Categoría:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        categorias = self.categoria_service.get_all()
        categoria_nombres = [c.nombre for c in categorias]
        self.categorias_dict = {c.nombre: c.id for c in categorias}
        
        self.categoria_var = ctk.StringVar(
            value=categoria_nombres[0] if categoria_nombres else "Sin categoría"
        )
        
        self.categoria_menu = ctk.CTkOptionMenu(
            main_frame,
            values=categoria_nombres,
            variable=self.categoria_var,
            font=("Arial", 14),
            fg_color="#2D5A27",
            button_color="#2D5A27",
            height=40
        )
        self.categoria_menu.pack(fill="x", pady=(0, 15))
        
        # Cargar datos si es edición
        if self.producto:
            self.nombre_entry.insert(0, self.producto.nombre)
            self.desc_entry.insert("1.0", self.producto.descripcion or "")
            self.precio_entry.insert(0, str(self.producto.precio))
            self.stock_entry.insert(0, str(self.producto.stock))
            
            if self.producto.categoria_id:
                for nombre, id in self.categorias_dict.items():
                    if id == self.producto.categoria_id:
                        self.categoria_var.set(nombre)
                        break
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            font=("Arial", 14, "bold"),
            fg_color="#FF6B35",
            hover_color="#E55A25",
            width=150,
            command=self.save
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=("Arial", 14),
            fg_color="gray",
            hover_color="#666",
            width=150,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=10)
    
    def save(self):
        """Guarda el producto"""
        nombre = self.nombre_entry.get().strip()
        descripcion = self.desc_entry.get("1.0", "end-1c").strip()
        precio_str = self.precio_entry.get().strip()
        stock_str = self.stock_entry.get().strip()
        categoria_nombre = self.categoria_var.get()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            precio = float(precio_str) if precio_str else 0.0
            stock = int(stock_str) if stock_str else 0
            categoria_id = self.categorias_dict.get(categoria_nombre)
            
            if self.producto:
                # Editar
                self.producto.nombre = nombre
                self.producto.descripcion = descripcion
                self.producto.precio = precio
                self.producto.stock = stock
                self.producto.categoria_id = categoria_id
                self.producto_service.update(self.producto)
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            else:
                # Crear
                nuevo_producto = Producto(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    stock=stock,
                    categoria_id=categoria_id
                )
                self.producto_service.create(nuevo_producto)
                messagebox.showinfo("Éxito", "Producto creado correctamente")
            
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class VentasView(ctk.CTkFrame):
    """Vista de sistema de facturación con carrito de compras"""
    
    def __init__(self, parent, producto_service, empresa_service, factura_service):
        super().__init__(parent, fg_color="#F5F5F5")
        self.producto_service = producto_service
        self.empresa_service = empresa_service
        self.factura_service = factura_service
        self.productos = []
        self.selected_producto = None
        self.cart_items = []  # Lista de items en el carrito
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets de la vista de facturación"""
        # Título y saldo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=40, fill="x")
        
        title = ctk.CTkLabel(
            header_frame,
            text="💳 Sistema de Facturación",
            font=("Arial", 28, "bold"),
            text_color="#2D5A27"
        )
        title.pack(side="left")
        
        presupuesto = self.empresa_service.get_presupuesto()
        self.presupuesto_label = ctk.CTkLabel(
            header_frame,
            text=f" Caja: ${presupuesto:,.2f}",
            font=("Arial", 18, "bold"),
            text_color=("#27ae60", "#2ecc71")
        )
        self.presupuesto_label.pack(side="right")
        
        # Frame principal dividido
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(pady=10, padx=40, fill="both", expand=True)
        main_container.grid_columnconfigure(0, weight=2)  # Selección
        main_container.grid_columnconfigure(1, weight=3)  # Carrito
        main_container.grid_rowconfigure(0, weight=1)
        
        # === PANEL IZQUIERDO: SELECCIÓN DE PRODUCTOS ===
        left_panel = ctk.CTkFrame(main_container, fg_color=("white", "#333333"), corner_radius=15)
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(
            left_panel,
            text="Selección de Productos",
            font=("Arial", 20, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        ).pack(pady=20)
        
        # Formulario de selección
        form_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        form_frame.pack(pady=10, padx=25, fill="both", expand=True)
        
        # Cliente
        ctk.CTkLabel(
            form_frame,
            text="Cliente:",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.cliente_entry = ctk.CTkEntry(
            form_frame,
            font=("Arial", 14),
            height=40,
            placeholder_text="Nombre del Cliente (opcional)"
        )
        self.cliente_entry.pack(fill="x", pady=(0, 20))
        
        # Producto
        ctk.CTkLabel(
            form_frame,
            text="Producto:",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.productos = self.producto_service.get_all()
        producto_nombres = [f"{p.nombre} - ${p.precio:.2f}" for p in self.productos]
        
        self.producto_var = ctk.StringVar(
            value=producto_nombres[0] if producto_nombres else "No hay productos"
        )
        
        self.producto_menu = ctk.CTkOptionMenu(
            form_frame,
            values=producto_nombres,
            variable=self.producto_var,
            font=("Arial", 14),
            fg_color="#2D5A27",
            button_color="#2D5A27",
            height=40,
            command=self.on_producto_selected
        )
        self.producto_menu.pack(fill="x", pady=(0, 10))
        
        # Stock disponible
        self.stock_label = ctk.CTkLabel(
            form_frame,
            text="Stock: -",
            font=("Arial", 12),
            text_color="gray"
        )
        self.stock_label.pack(anchor="w", pady=(0, 15))
        
        # Cantidad
        ctk.CTkLabel(
            form_frame,
            text="Cantidad:",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.cantidad_entry = ctk.CTkEntry(
            form_frame,
            font=("Arial", 14),
            height=40,
            placeholder_text="0"
        )
        self.cantidad_entry.pack(fill="x", pady=(0, 20))
        
        # Botón Agregar al Carrito
        add_to_cart_btn = ctk.CTkButton(
            form_frame,
            text="🛒 Agregar al Carrito",
            font=("Arial", 16, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=50,
            command=self.agregar_al_carrito
        )
        add_to_cart_btn.pack(fill="x", pady=20)
        
        # Inicializar con el primer producto
        if self.productos:
            self.on_producto_selected(self.producto_var.get())
        
        # === PANEL DERECHO: CARRITO DE COMPRAS ===
        right_panel = ctk.CTkFrame(main_container, fg_color=("white", "#333333"), corner_radius=15)
        right_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        ctk.CTkLabel(
            right_panel,
            text="🛒 Carrito de Compras",
            font=("Arial", 20, "bold"),
            text_color=("#2D5A27", "#2ecc71")
        ).pack(pady=20)
        
        # Área del carrito
        self.cart_scroll = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=("#F5F5F5", "#2b2b2b")
        )
        self.cart_scroll.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Total
        total_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        total_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(
            total_frame,
            text="TOTAL A PAGAR:",
            font=("Arial", 18, "bold"),
            text_color="#2D5A27"
        ).pack(side="left")
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="$0.00",
            font=("Arial", 28, "bold"),
            text_color="#27ae60"
        )
        self.total_label.pack(side="right")
        
        # === CÁLCULO DE CAMBIO ===
        cambio_section = ctk.CTkFrame(right_panel, fg_color="transparent")
        cambio_section.pack(pady=10, padx=20, fill="x")
        
        # Efectivo recibido
        efectivo_frame = ctk.CTkFrame(cambio_section, fg_color="transparent")
        efectivo_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            efectivo_frame,
            text="Efectivo Recibido:",
            font=("Arial", 14, "bold"),
            text_color="#2D5A27"
        ).pack(side="left")
        
        self.efectivo_entry = ctk.CTkEntry(
            efectivo_frame,
            font=("Arial", 14),
            height=40,
            width=150,
            placeholder_text="$0.00"
        )
        self.efectivo_entry.pack(side="right")
        self.efectivo_entry.bind("<KeyRelease>", self.calcular_cambio)
        
        # Cambio a devolver
        cambio_frame = ctk.CTkFrame(cambio_section, fg_color="transparent")
        cambio_frame.pack(fill="x")
        
        ctk.CTkLabel(
            cambio_frame,
            text="Cambio a devolver:",
            font=("Arial", 14, "bold"),
            text_color="#2D5A27"
        ).pack(side="left")
        
        self.cambio_label = ctk.CTkLabel(
            cambio_frame,
            text="$0.00",
            font=("Arial", 16, "bold"),
            text_color="#27ae60"
        )
        self.cambio_label.pack(side="right")
        
        # Botón Finalizar Venta
        finalizar_btn = ctk.CTkButton(
            right_panel,
            text="💳 Finalizar Venta / Facturar",
            font=("Arial", 18, "bold"),
            fg_color="#FF6B35",
            hover_color="#E55A25",
            height=60,
            command=self.finalizar_venta
        )
        finalizar_btn.pack(pady=20, padx=20, fill="x")
        
        self.update_cart_display()
    
    def on_producto_selected(self, selection):
        """Maneja la selección de un producto"""
        nombre_producto = selection.split(" - ")[0]
        
        self.selected_producto = None
        for p in self.productos:
            if p.nombre == nombre_producto:
                self.selected_producto = p
                break
        
        if self.selected_producto:
            self.stock_label.configure(
                text=f"Stock: {self.selected_producto.stock} unidades"
            )
    
    def calcular_cambio(self, event=None):
        """Calcula el cambio a devolver basado en el efectivo recibido"""
        try:
            efectivo = float(self.efectivo_entry.get() or 0)
            total = sum(item['subtotal'] for item in self.cart_items)
            cambio = efectivo - total
            
            if cambio < 0:
                # Efectivo insuficiente - mostrar falta en rojo
                self.cambio_label.configure(
                    text=f"Falta: ${abs(cambio):,.2f}",
                    text_color="#e74c3c"
                )
            else:
                # Mostrar cambio en verde
                self.cambio_label.configure(
                    text=f"Cambio: ${cambio:,.2f}",
                    text_color="#27ae60"
                )
        except ValueError:
            self.cambio_label.configure(
                text="$0.00",
                text_color="#27ae60"
            )
    
    def agregar_al_carrito(self):
        """Agrega un producto al carrito"""
        if not self.selected_producto:
            messagebox.showerror("Error", "Debe seleccionar un producto")
            return
        
        try:
            cantidad = int(self.cantidad_entry.get() or 0)
            
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            if cantidad > self.selected_producto.stock:
                messagebox.showerror(
                    "Stock Insuficiente",
                    f"No hay suficiente stock.\nDisponible: {self.selected_producto.stock}"
                )
                return
            
            # Verificar si el producto ya está en el carrito
            for item in self.cart_items:
                if item['producto_id'] == self.selected_producto.id:
                    # Actualizar cantidad
                    nueva_cantidad = item['cantidad'] + cantidad
                    if nueva_cantidad > self.selected_producto.stock:
                        messagebox.showerror(
                            "Stock Insuficiente",
                            f"Ya tiene {item['cantidad']} en el carrito.\n"
                            f"No puede agregar {cantidad} más."
                        )
                        return
                    item['cantidad'] = nueva_cantidad
                    item['subtotal'] = nueva_cantidad * item['precio_unitario']
                    self.cantidad_entry.delete(0, 'end')
                    self.update_cart_display()
                    return
            
            # Agregar nuevo item al carrito
            cart_item = {
                'producto_id': self.selected_producto.id,
                'producto_nombre': self.selected_producto.nombre,
                'cantidad': cantidad,
                'precio_unitario': self.selected_producto.precio,
                'subtotal': cantidad * self.selected_producto.precio
            }
            self.cart_items.append(cart_item)
            
            # Limpiar cantidad
            self.cantidad_entry.delete(0, 'end')
            
            # Actualizar vista del carrito
            self.update_cart_display()
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
    
    def eliminar_del_carrito(self, index):
        """Elimina un item del carrito"""
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)
            self.update_cart_display()
    
    def update_cart_display(self):
        """Actualiza la visualización del carrito"""
        # Limpiar carrito
        for widget in self.cart_scroll.winfo_children():
            widget.destroy()
        
        if not self.cart_items:
            ctk.CTkLabel(
                self.cart_scroll,
                text="Carrito vacío\nAgrega productos para facturar",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=40)
            self.total_label.configure(text="$0.00")
            return
        
        # Mostrar items
        for idx, item in enumerate(self.cart_items):
            item_frame = ctk.CTkFrame(self.cart_scroll, fg_color=("#F5F5F5", "#2b2b2b"))
            item_frame.pack(fill="x", pady=5, padx=10)
            
            # Contenido del item
            content = ctk.CTkFrame(item_frame, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            
            # Nombre del producto
            ctk.CTkLabel(
                content,
                text=item['producto_nombre'],
                font=("Arial", 14, "bold"),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
            
            # Subtotal
            ctk.CTkLabel(
                content,
                text=f"${item['subtotal']:,.2f}",
                font=("Arial", 14, "bold"),
                text_color="#27ae60"
            ).pack(side="right", padx=10)
            
            # Botón eliminar
            delete_btn = ctk.CTkButton(
                content,
                text="🗑️",
                font=("Arial", 12),
                fg_color="#e74c3c",
                hover_color="#c0392b",
                width=40,
                command=lambda i=idx: self.eliminar_del_carrito(i)
            )
            delete_btn.pack(side="right")
            
            # Detalles
            details = ctk.CTkFrame(item_frame, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(
                details,
                text=f"Cantidad: {item['cantidad']} × ${item['precio_unitario']:.2f}",
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            ).pack(side="left")
        
        # Calcular y mostrar total
        total = sum(item['subtotal'] for item in self.cart_items)
        self.total_label.configure(text=f"${total:,.2f}")
    
    def finalizar_venta(self):
        """Procesa la factura completa"""
        if not self.cart_items:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        # Obtener nombre del cliente
        cliente = self.cliente_entry.get().strip()
        if not cliente:
            cliente = "Consumidor Final"
        
        # Calcular total
        total = sum(item['subtotal'] for item in self.cart_items)
        
        # Validar stock para todos los items
        for item in self.cart_items:
            producto = self.producto_service.get_by_id(item['producto_id'])
            if not producto or producto.stock < item['cantidad']:
                messagebox.showerror(
                    "Stock Insuficiente",
                    f"No hay suficiente stock de '{item['producto_nombre']}'.\n"
                    f"Disponible: {producto.stock if producto else 0}\n"
                    f"Requerido: {item['cantidad']}"
                )
                return
        
        # Confirmar venta
        if not messagebox.askyesno(
            "Confirmar Factura",
            f"Cliente: {cliente}\n"
            f"Total de items: {len(self.cart_items)}\n"
            f"Total: ${total:,.2f}\n\n"
            f"¿Desea confirmar la factura?"
        ):
            return
        
        try:
            # Crear factura y detalles
            from models import Factura, DetalleFactura
            
            factura = Factura(cliente=cliente, total=total)
            detalles = []
            
            for item in self.cart_items:
                detalle = DetalleFactura(
                    producto_id=item['producto_id'],
                    producto_nombre=item['producto_nombre'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                    subtotal=item['subtotal']
                )
                detalles.append(detalle)
            
            # Guardar factura completa (actualiza stock y presupuesto)
            self.factura_service.crear_factura_completa(
                factura,
                detalles,
                self.producto_service,
                self.empresa_service
            )
            
            # Mostrar éxito
            messagebox.showinfo(
                "Factura Exitosa",
                f"Factura #{factura.id} creada correctamente\n\n"
                f"Cliente: {cliente}\n"
                f"Total: ${total:,.2f}\n"
                f"Nuevo saldo: ${self.empresa_service.get_presupuesto():,.2f}"
            )
            
            # Limpiar formulario y carrito
            self.cliente_entry.delete(0, 'end')
            self.cantidad_entry.delete(0, 'end')
            self.cart_items = []
            
            # Actualizar productos y carrito
            self.productos = self.producto_service.get_all()
            if self.productos:
                producto_nombres = [f"{p.nombre} - ${p.precio:.2f}" for p in self.productos]
                self.producto_menu.configure(values=producto_nombres)
                self.producto_var.set(producto_nombres[0])
                self.on_producto_selected(producto_nombres[0])
            
            self.update_cart_display()
            self.update_presupuesto_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la factura: {str(e)}")
    
    def update_presupuesto_display(self):
        """Actualiza el display del presupuesto"""
        presupuesto = self.empresa_service.get_presupuesto()
        self.presupuesto_label.configure(text=f"Caja: ${presupuesto:,.2f}")
    
    def refresh(self):
        """Refresca la vista"""
        for widget in self.winfo_children():
            widget.destroy()
        self.cart_items = []
        self.create_widgets()


class HistorialView(ctk.CTkFrame):
    """Vista de historial de ventas (Facturas)"""
    
    def __init__(self, parent, factura_service):
        super().__init__(parent, fg_color=("#F5F5F5", "#2b2b2b"))
        self.factura_service = factura_service
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets"""
        # Título
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=40, fill="x")
        
        title = ctk.CTkLabel(
            header_frame,
            text="📜 Historial de Ventas",
            font=("Arial", 28, "bold"),
            text_color="#2D5A27"
        )
        title.pack(side="left")
        
        # Botón Limpiar Historial
        clear_btn = ctk.CTkButton(
            header_frame,
            text="🗑️ Limpiar Historial",
            font=("Arial", 14, "bold"),
            fg_color="#c0392b",
            hover_color="#a93226",
            command=self.limpiar_historial
        )
        clear_btn.pack(side="right")
        
        # Tabla
        self.table_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("white", "#333333"),
            corner_radius=15
        )
        self.table_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        self.load_historial()
    
    def load_historial(self):
        """Carga el historial de facturas"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Encabezados
        headers = ["ID Factura", "Fecha", "Cliente", "Total", "Acciones"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="#2D5A27")
        header_frame.pack(fill="x", pady=(0, 10))
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="white"
            )
            label.grid(row=0, column=i, padx=20, pady=15, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Datos
        facturas = self.factura_service.get_historial(limit=50) # Limitar a las últimas 50 para rendimiento
        
        if not facturas:
            ctk.CTkLabel(
                self.table_frame,
                text="No hay ventas registradas",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
            return
        
        for idx, factura in enumerate(facturas):
            bg_color = ("#F5F5F5", "#2b2b2b") if idx % 2 == 0 else ("white", "#333333")
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color)
            row_frame.pack(fill="x", pady=2)
            
            # ID
            self._create_cell(row_frame, f"#{factura.id}", 0)
            # Fecha (cortar timestamp si es muy largo)
            fecha_str = str(factura.fecha).split('.')[0]
            self._create_cell(row_frame, fecha_str, 1)
            # Cliente
            self._create_cell(row_frame, factura.cliente, 2)
            # Total
            total_label = ctk.CTkLabel(
                row_frame,
                text=f"${factura.total:,.2f}",
                font=("Arial", 12, "bold"),
                text_color=("#27ae60", "#2ecc71"),
                anchor="w"
            )
            total_label.grid(row=0, column=3, padx=20, pady=10, sticky="w")
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=4, padx=20, pady=5)
            
            view_btn = ctk.CTkButton(
                actions_frame,
                text="👁️ Ver Detalle",
                font=("Arial", 11),
                fg_color="#3498db",
                hover_color="#2980b9",
                width=100,
                command=lambda f=factura: self.ver_detalle(f)
            )
            view_btn.pack()
            
            # Configurar columnas
            for i in range(5):
                row_frame.grid_columnconfigure(i, weight=1)
    
    def _create_cell(self, parent, text, col):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Arial", 12),
            anchor="w",
            text_color=("black", "white")
        ).grid(row=0, column=col, padx=20, pady=10, sticky="w")
    
    def ver_detalle(self, factura):
        """Muestra el detalle de una factura"""
        detalles = self.factura_service.get_detalles_factura(factura.id)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Detalle Factura #{factura.id}")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Info cabecera
        info_frame = ctk.CTkFrame(dialog, fg_color=("#F5F5F5", "#2b2b2b"))
        info_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(info_frame, text=f"Cliente: {factura.cliente}", font=("Arial", 12, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(info_frame, text=f"Total: ${factura.total:,.2f}", font=("Arial", 12, "bold"), text_color=("#27ae60", "#2ecc71")).pack(side="right", padx=20)
        
        # Lista productos
        scroll = ctk.CTkScrollableFrame(dialog, fg_color=("white", "#333333"))
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for d in detalles:
            f = ctk.CTkFrame(scroll, fg_color=("#F5F5F5", "#2b2b2b"))
            f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=f"{d.cantidad} x {d.producto_nombre}", anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(f, text=f"${d.subtotal:,.2f}", anchor="e").pack(side="right", padx=10)
            
    def limpiar_historial(self):
        """Limpia el historial de ventas"""
        if messagebox.askyesno("Seguridad", "ATENCIÓN: Esto borrará permanentemente todas las facturas.\n\nEl dinero en Caja NO se verá afectado, pero perderá el registro de qué se vendió.\n\n¿Está seguro?"):
            contrasena = ctk.CTkInputDialog(text="Ingrese contraseña de admin para confirmar:", title="Seguridad").get_input()
            if contrasena == "admin123": # Contraseña hardcoded simple
                self.factura_service.limpiar_historial()
                self.load_historial()
                messagebox.showinfo("Éxito", "Historial eliminado")
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
    
    def refresh(self):
        self.load_historial()
