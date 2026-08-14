"""
Capa de Acceso a Datos (DataService).
Maneja la conexión y operaciones con la base de datos SQLite.
"""

import sqlite3
import os


class DataService:
    """Servicio de acceso a la base de datos SQLite"""
    
    def __init__(self, db_name="distribuidora.db"):
        """
        Inicializa el servicio de base de datos
        
        Args:
            db_name: Nombre del archivo de base de datos
        """
        # Obtener la ruta del directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, db_name)
        self.connection = None
        self._initialize_database()
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return self.connection
    
    def _initialize_database(self):
        """Crea las tablas si no existen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT
            )
        ''')
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL DEFAULT 0.0,
                stock INTEGER NOT NULL DEFAULT 0,
                categoria_id INTEGER,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
            )
        ''')
        
        # Tabla de empresa (presupuesto/caja)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                presupuesto REAL NOT NULL DEFAULT 0.0
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        
        # Tabla de historial de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                producto_nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                total REAL NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
            )
        ''')
        
        # Tabla de facturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL DEFAULT 'Consumidor Final',
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total REAL NOT NULL
            )
        ''')
        
        # Tabla de detalle de factura
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_factura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_factura INTEGER NOT NULL,
                producto_id INTEGER,
                producto_nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_factura) REFERENCES facturas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        
        # Insertar datos de ejemplo si las tablas están vacías
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data()
        
        # Insertar empresa por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM empresa")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO empresa (nombre, presupuesto) VALUES (?, ?)",
                ("Distribuidora Principal", 10000.0)
            )
            conn.commit()
    
    def _insert_sample_data(self):
        """Inserta datos de ejemplo en la base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Categorías de ejemplo
        categorias = [
            ("Carnes", "Productos cárnicos frescos y procesados"),
            ("Verduras", "Verduras y hortalizas frescas"),
            ("Frutas", "Frutas frescas de temporada"),
            ("Lácteos", "Productos lácteos y derivados"),
            ("Panadería", "Pan y productos de panadería")
        ]
        
        cursor.executemany(
            "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
            categorias
        )
        
        # Productos de ejemplo
        productos = [
            ("Carne de Res", "Carne de res fresca premium", 150.00, 50, 1),
            ("Pollo Entero", "Pollo fresco de granja", 80.00, 100, 1),
            ("Lechuga", "Lechuga fresca orgánica", 15.00, 200, 2),
            ("Tomate", "Tomate rojo fresco", 20.00, 150, 2),
            ("Manzana", "Manzana roja importada", 35.00, 120, 3),
            ("Leche", "Leche entera 1L", 25.00, 80, 4),
            ("Pan Blanco", "Pan blanco artesanal", 30.00, 50, 5)
        ]
        
        cursor.executemany(
            "INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id) VALUES (?, ?, ?, ?, ?)",
            productos
        )
        
        conn.commit()
    
    def execute_query(self, query, params=()):
        """
        Ejecuta una consulta SQL (INSERT, UPDATE, DELETE)
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            ID del último registro insertado
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    
    def fetch_all(self, query, params=()):
        """
        Ejecuta una consulta SELECT y retorna todos los resultados
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convertir Row objects a diccionarios
        return [dict(row) for row in rows]
    
    def fetch_one(self, query, params=()):
        """
        Ejecuta una consulta SELECT y retorna un solo resultado
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None
