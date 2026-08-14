"""
Capa de Servicios - Lógica de Negocio.
Separa la lógica de negocio de la interfaz de usuario y la base de datos.
"""

from database import DataService
from models import Categoria, Producto, Factura, DetalleFactura


class CategoriaService:
    """Servicio para gestionar categorías"""
    
    def __init__(self, data_service: DataService):
        self.db = data_service
    
    def get_all(self):
        """Obtiene todas las categorías"""
        query = "SELECT * FROM categorias ORDER BY nombre"
        rows = self.db.fetch_all(query)
        return [Categoria.from_dict(row) for row in rows]
    
    def get_by_id(self, categoria_id):
        """Obtiene una categoría por ID"""
        query = "SELECT * FROM categorias WHERE id = ?"
        row = self.db.fetch_one(query, (categoria_id,))
        return Categoria.from_dict(row) if row else None
    
    def create(self, categoria: Categoria):
        """Crea una nueva categoría"""
        query = "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)"
        categoria_id = self.db.execute_query(
            query,
            (categoria.nombre, categoria.descripcion)
        )
        categoria.id = categoria_id
        return categoria
    
    def update(self, categoria: Categoria):
        """Actualiza una categoría existente"""
        query = "UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?"
        self.db.execute_query(
            query,
            (categoria.nombre, categoria.descripcion, categoria.id)
        )
        return categoria
    
    def delete(self, categoria_id):
        """Elimina una categoría"""
        query = "DELETE FROM categorias WHERE id = ?"
        self.db.execute_query(query, (categoria_id,))
    
    def get_count(self):
        """Obtiene el número total de categorías"""
        query = "SELECT COUNT(*) as count FROM categorias"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0


class ProductoService:
    """Servicio para gestionar productos"""
    
    def __init__(self, data_service: DataService):
        self.db = data_service
    
    def get_all(self):
        """Obtiene todos los productos"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nombre
        """
        rows = self.db.fetch_all(query)
        productos = []
        for row in rows:
            producto = Producto.from_dict(row)
            producto.categoria_nombre = row.get('categoria_nombre', 'Sin categoría')
            productos.append(producto)
        return productos
    
    def get_by_id(self, producto_id):
        """Obtiene un producto por ID"""
        query = "SELECT * FROM productos WHERE id = ?"
        row = self.db.fetch_one(query, (producto_id,))
        return Producto.from_dict(row) if row else None
    
    def create(self, producto: Producto):
        """Crea un nuevo producto"""
        query = """
            INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id)
            VALUES (?, ?, ?, ?, ?)
        """
        producto_id = self.db.execute_query(
            query,
            (producto.nombre, producto.descripcion, producto.precio, 
             producto.stock, producto.categoria_id)
        )
        producto.id = producto_id
        return producto
    
    def update(self, producto: Producto):
        """Actualiza un producto existente"""
        query = """
            UPDATE productos 
            SET nombre = ?, descripcion = ?, precio = ?, stock = ?, categoria_id = ?
            WHERE id = ?
        """
        self.db.execute_query(
            query,
            (producto.nombre, producto.descripcion, producto.precio,
             producto.stock, producto.categoria_id, producto.id)
        )
        return producto
    
    def delete(self, producto_id):
        """Elimina un producto"""
        query = "DELETE FROM productos WHERE id = ?"
        self.db.execute_query(query, (producto_id,))
    
    def search(self, search_term):
        """Busca productos por nombre o descripción"""
        query = """
            SELECT p.*, c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.nombre LIKE ? OR p.descripcion LIKE ?
            ORDER BY p.nombre
        """
        search_pattern = f"%{search_term}%"
        rows = self.db.fetch_all(query, (search_pattern, search_pattern))
        productos = []
        for row in rows:
            producto = Producto.from_dict(row)
            producto.categoria_nombre = row.get('categoria_nombre', 'Sin categoría')
            productos.append(producto)
        return productos
    
    def get_count(self):
        """Obtiene el número total de productos"""
        query = "SELECT COUNT(*) as count FROM productos"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0

    def get_low_stock(self, threshold=5):
        """Obtiene productos con stock bajo"""
        query = "SELECT * FROM productos WHERE stock < ?"
        rows = self.db.fetch_all(query, (threshold,))
        return [Producto.from_dict(row) for row in rows]
    
    def get_total_value(self):
        """Obtiene el valor total del inventario"""
        query = "SELECT SUM(precio * stock) as total FROM productos"
        result = self.db.fetch_one(query)
        return result['total'] if result and result['total'] else 0.0



class EmpresaService:
    """Servicio para gestionar datos de la empresa"""
    
    def __init__(self, data_service: DataService):
        self.db = data_service
    
    def get_presupuesto(self):
        """Obtiene el presupuesto/saldo actual de la empresa"""
        query = "SELECT presupuesto FROM empresa WHERE id = 1"
        result = self.db.fetch_one(query)
        return result['presupuesto'] if result else 0.0
    
    def actualizar_presupuesto(self, monto):
        """Actualiza el presupuesto sumando el monto especificado"""
        query = "UPDATE empresa SET presupuesto = presupuesto + ? WHERE id = 1"
        self.db.execute_query(query, (monto,))
    
    def get_datos_empresa(self):
        """Obtiene todos los datos de la empresa"""
        query = "SELECT * FROM empresa WHERE id = 1"
        return self.db.fetch_one(query)
    
    def establecer_presupuesto(self, nuevo_monto):
        """Establece un nuevo presupuesto (reemplazo total)"""
        query = "UPDATE empresa SET presupuesto = ? WHERE id = 1"
        self.db.execute_query(query, (nuevo_monto,))





class FacturaService:
    """Servicio para gestionar facturas"""
    
    def __init__(self, data_service: DataService):
        self.db = data_service
    
    def crear_factura_completa(self, factura: Factura, detalles: list, producto_service, empresa_service):
        """
        Crea una factura completa con todos sus detalles en una transacción
        
        Args:
            factura: Objeto Factura con datos del cliente y total
            detalles: Lista de objetos DetalleFactura
            producto_service: Servicio de productos para actualizar stock
            empresa_service: Servicio de empresa para actualizar presupuesto
        """
        try:
            # Crear la factura
            query_factura = """
                INSERT INTO facturas (cliente, total)
                VALUES (?, ?)
            """
            factura_id = self.db.execute_query(
                query_factura,
                (factura.cliente, factura.total)
            )
            factura.id = factura_id
            
            # Insertar cada detalle
            query_detalle = """
                INSERT INTO detalle_factura 
                (id_factura, producto_id, producto_nombre, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            for detalle in detalles:
                detalle.id_factura = factura_id
                self.db.execute_query(
                    query_detalle,
                    (factura_id, detalle.producto_id, detalle.producto_nombre,
                     detalle.cantidad, detalle.precio_unitario, detalle.subtotal)
                )
                
                # Actualizar stock del producto
                producto = producto_service.get_by_id(detalle.producto_id)
                if producto:
                    producto.stock -= detalle.cantidad
                    producto_service.update(producto)
            
            # Actualizar presupuesto de la empresa
            empresa_service.actualizar_presupuesto(factura.total)
            
            return factura
            
        except Exception as e:
            raise Exception(f"Error al crear factura: {str(e)}")
    
    def get_historial(self, limit=None):
        """Obtiene el historial de facturas"""
        query = """
            SELECT * FROM facturas 
            ORDER BY fecha DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        rows = self.db.fetch_all(query)
        return [Factura.from_dict(row) for row in rows]
    
    def get_detalles_factura(self, id_factura):
        """Obtiene todos los detalles de una factura"""
        query = """
            SELECT * FROM detalle_factura 
            WHERE id_factura = ?
            ORDER BY id
        """
        rows = self.db.fetch_all(query, (id_factura,))
        return [DetalleFactura.from_dict(row) for row in rows]
    
    def get_total_facturas(self):
        """Obtiene el total facturado"""
        query = "SELECT SUM(total) as total FROM facturas"
        result = self.db.fetch_one(query)
        return result['total'] if result and result['total'] else 0.0
    
    def get_total_ventas_hoy(self):
        """Obtiene el total de ventas (facturas) del día actual (zona horaria local)"""
        # SQLite 'now', 'localtime' convierte UTC a hora local del sistema
        query = "SELECT SUM(total) as total FROM facturas WHERE date(fecha, 'localtime') = date('now', 'localtime')"
        result = self.db.fetch_one(query)
        return result['total'] if result and result['total'] else 0.0
    
    def get_count(self):
        """Obtiene el número total de facturas"""
        query = "SELECT COUNT(*) as count FROM facturas"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0
    
    def limpiar_historial(self):
        """Elimina todas las facturas y sus detalles"""
        self.db.execute_non_query("DELETE FROM detalle_factura")
        self.db.execute_non_query("DELETE FROM facturas")


class ConfigService:
    """Servicio para gestionar la configuración persistente"""
    
    def __init__(self, data_service: DataService):
        self.db = data_service
    
    def get_config(self, clave, default=None):
        """Obtiene un valor de configuración"""
        query = "SELECT valor FROM configuracion WHERE clave = ?"
        result = self.db.fetch_one(query, (clave,))
        return result['valor'] if result else default
    
    def set_config(self, clave, valor):
        """Guarda un valor de configuración"""
        query = "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)"
        self.db.execute_query(query, (clave, str(valor)))
    
    def limpiar_historial(self):
        """Elimina todas las facturas y detalles (no afecta presupuesto ni stock)"""
        # Primero eliminar detalles (por seguridad, aunque CASCADE debería hacerlo)
        self.db.execute_query("DELETE FROM detalle_factura")
        # Luego eliminar facturas
        self.db.execute_query("DELETE FROM facturas")


