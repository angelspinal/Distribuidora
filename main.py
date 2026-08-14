"""
Aplicación Principal de Distribuidora
Sistema de gestión de inventario con interfaz moderna usando CustomTkinter
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
from database import DataService
from services import CategoriaService, ProductoService, EmpresaService, FacturaService, ConfigService
from views import DashboardView, ProductosView, CategoriasView, AjustesView, VentasView, HistorialView


class DistribuidoraApp(ctk.CTk):
    """Aplicación principal con navegación lateral"""
    
    def __init__(self, config_service=None):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Distribuidora - Sistema de Gestión")
        self.geometry("1200x700")
        
        # Inicializar servicios
        self.db_service = DataService()
        self.categoria_service = CategoriaService(self.db_service)
        self.producto_service = ProductoService(self.db_service)
        self.empresa_service = EmpresaService(self.db_service)
        self.factura_service = FacturaService(self.db_service)
        self.config_service = config_service if config_service else ConfigService(self.db_service)
        
        # Configurar tema según persistencia
        saved_theme = self.config_service.get_config("modo", "Light")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("green")
        
        # Inicializar servicios
        self.db_service = DataService()
        self.categoria_service = CategoriaService(self.db_service)
        self.producto_service = ProductoService(self.db_service)
        self.empresa_service = EmpresaService(self.db_service)
        self.factura_service = FacturaService(self.db_service)
        
        # Variables
        self.current_view = None
        
        # Crear interfaz
        self.create_layout()
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def create_layout(self):
        """Crea el layout principal con sidebar y contenido"""
        # Configurar grid para expansión correcta
        self.grid_columnconfigure(0, weight=0)  # Sidebar fijo
        self.grid_columnconfigure(1, weight=1)  # Contenido expandible
        self.grid_rowconfigure(0, weight=1)  # Fila expandible
        
        # === SIDEBAR (Barra Lateral de Navegación) ===
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color="#2D5A27",
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo/Título
        try:
            # Cargar imagen
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
            pil_image = Image.open(image_path)
            
            # Icono de ventana
            self.iconphoto(False, ImageTk.PhotoImage(pil_image))
            
            # Imagen para sidebar (redimensionar)
            logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))
            
            logo_label = ctk.CTkLabel(
                self.sidebar,
                text="",
                image=logo_img
            )
            logo_label.pack(pady=(30, 10))
            
            # Texto debajo del logo
            ctk.CTkLabel(
                self.sidebar,
                text="VENTRO",
                font=("Arial", 20, "bold"),
                text_color="white"
            ).pack(pady=(0, 20))
            
        except Exception as e:
            # Fallback si falla la imagen
            print(f"No se pudo cargar el logo: {e}")
            logo_label = ctk.CTkLabel(
                self.sidebar,
                text="🏪 DISTRIBUIDORA",
                font=("Arial", 24, "bold"),
                text_color="white"
            )
            logo_label.pack(pady=30)
        
        # Separador
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="white")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Botones de navegación
        self.nav_buttons = []
        
        self.create_nav_button("📊 Dashboard", self.show_dashboard)
        self.create_nav_button("📦 Productos", self.show_productos)
        self.create_nav_button("🏷️ Categorías", self.show_categorias)
        self.create_nav_button("💰 Ventas", self.show_ventas)
        self.create_nav_button("📜 Historial", self.show_historial)
        self.create_nav_button("⚙️ Ajustes", self.show_ajustes)
        
        # Espacio flexible
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(expand=True)
        
        # Información del sistema en la parte inferior
        info_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0\n© 2024",
            font=("Arial", 10),
            text_color="white"
        )
        info_label.pack(pady=20)
        
        # === CONTENEDOR DE CONTENIDO ===
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="#F5F5F5",
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
    
    def create_nav_button(self, text, command):
        """Crea un botón de navegación en el sidebar"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            font=("Arial", 16, "bold"),
            fg_color="transparent",
            hover_color="#1F4019",
            text_color="white",
            anchor="center",
            height=50,
            command=command
        )
        btn.pack(fill="x", padx=15, pady=5)
        self.nav_buttons.append(btn)
        return btn
    
    def highlight_button(self, active_button):
        """Resalta el botón activo"""
        for btn in self.nav_buttons:
            if btn == active_button:
                btn.configure(fg_color="#FF6B35")
            else:
                btn.configure(fg_color="transparent")
    
    def clear_content(self):
        """Limpia el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Muestra la vista del Dashboard"""
        self.clear_content()
        self.current_view = DashboardView(
            self.content_frame,
            self.categoria_service,
            self.producto_service,
            self.empresa_service,
            self.factura_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[0])
    
    def show_productos(self):
        """Muestra la vista de Productos"""
        self.clear_content()
        self.current_view = ProductosView(
            self.content_frame,
            self.categoria_service,
            self.producto_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[1])
    
    def show_categorias(self):
        """Muestra la vista de Categorías"""
        self.clear_content()
        self.current_view = CategoriasView(
            self.content_frame,
            self.categoria_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[2])
    
    def show_ventas(self):
        """Muestra la vista de Ventas"""
        self.clear_content()
        self.current_view = VentasView(
            self.content_frame,
            self.producto_service,
            self.empresa_service,
            self.factura_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[3])
    
    def show_historial(self):
        """Muestra la vista de Historial"""
        self.clear_content()
        self.current_view = HistorialView(
            self.content_frame,
            self.factura_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[4])

    def show_ajustes(self):
        """Muestra la vista de Ajustes"""
        self.clear_content()
        self.current_view = AjustesView(
            self.content_frame, 
            self.empresa_service,
            self.config_service
        )
        self.current_view.pack(fill="both", expand=True)
        self.highlight_button(self.nav_buttons[5])
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.db_service.close()
        self.destroy()


class LoginWindow(ctk.CTk):
    """Ventana de Login Simple"""
    def __init__(self):
        super().__init__()
        self.title("Acceso Distribuidora")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Centrar en pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"400x300+{x}+{y}")
        
        self.authenticated = False
        
        # Widgets
        # Intentar cargar logo en login también
        try:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
            pil_image = Image.open(image_path)
            self.iconphoto(False, ImageTk.PhotoImage(pil_image))
            
            logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(80, 80))
            ctk.CTkLabel(self, text="", image=logo_img).pack(pady=(20, 10))
        except:
            pass
            
        ctk.CTkLabel(self, text="🔒 Acceso Seguro", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=200)
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", self.login)
        
        ctk.CTkButton(self, text="Entrar", command=self.login, fg_color="#2D5A27").pack(pady=20)
        
        ctk.CTkLabel(self, text="(Clave por defecto: admin123)", text_color="gray").pack(pady=5)

    def login(self, event=None):
        if self.password_entry.get() == "admin123":
            self.authenticated = True
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Contraseña incorrecta")

def main():
    """Función principal - punto de entrada de la aplicación"""
    # Inicializar servicio de configuración
    db_service = DataService()
    config_service = ConfigService(db_service)
    
    # Cargar tema guardado
    saved_theme = config_service.get_config("modo", "Light")
    ctk.set_appearance_mode(saved_theme)
    ctk.set_default_color_theme("green")
    
    # Seguridad primero
    login = LoginWindow()
    login.mainloop()
    
    if login.authenticated:
        app = DistribuidoraApp(config_service=config_service)
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()

if __name__ == "__main__":
    main()
