"""
Modelos de datos para la aplicación de Distribuidora.
Representa las entidades del negocio: Categoría y Producto.
"""

class Categoria:
    """Modelo para representar una categoría de productos"""
    
    def __init__(self, id=None, nombre="", descripcion=""):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Categoria desde un diccionario"""
        return Categoria(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', '')
        )
    
    def __str__(self):
        return f"Categoria(id={self.id}, nombre='{self.nombre}')"


class Producto:
    """Modelo para representar un producto"""
    
    def __init__(self, id=None, nombre="", descripcion="", precio=0.0, stock=0, categoria_id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.categoria_id = categoria_id
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'stock': self.stock,
            'categoria_id': self.categoria_id
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Producto desde un diccionario"""
        return Producto(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            precio=float(data.get('precio', 0.0)),
            stock=int(data.get('stock', 0)),
            categoria_id=data.get('categoria_id')
        )
    
    def __str__(self):
        return f"Producto(id={self.id}, nombre='{self.nombre}', precio={self.precio})"





class Factura:
    """Modelo para representar una factura"""
    
    def __init__(self, id=None, cliente="Consumidor Final", fecha=None, total=0.0):
        self.id = id
        self.cliente = cliente
        self.fecha = fecha
        self.total = total
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'cliente': self.cliente,
            'fecha': self.fecha,
            'total': self.total
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Factura desde un diccionario"""
        return Factura(
            id=data.get('id'),
            cliente=data.get('cliente', 'Consumidor Final'),
            fecha=data.get('fecha'),
            total=float(data.get('total', 0.0))
        )
    
    def __str__(self):
        return f"Factura(id={self.id}, cliente='{self.cliente}', total={self.total})"


class DetalleFactura:
    """Modelo para representar un detalle de factura"""
    
    def __init__(self, id=None, id_factura=None, producto_id=None, 
                 producto_nombre="", cantidad=0, precio_unitario=0.0, subtotal=0.0):
        self.id = id
        self.id_factura = id_factura
        self.producto_id = producto_id
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'id_factura': self.id_factura,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto_nombre,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto DetalleFactura desde un diccionario"""
        return DetalleFactura(
            id=data.get('id'),
            id_factura=data.get('id_factura'),
            producto_id=data.get('producto_id'),
            producto_nombre=data.get('producto_nombre', ''),
            cantidad=int(data.get('cantidad', 0)),
            precio_unitario=float(data.get('precio_unitario', 0.0)),
            subtotal=float(data.get('subtotal', 0.0))
        )
    
    def __str__(self):
        return f"DetalleFactura(factura={self.id_factura}, producto='{self.producto_nombre}', subtotal={self.subtotal})"


