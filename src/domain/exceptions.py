"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""

from typing import Optional


class ProductNotFoundError(Exception):
    """
    Se lanza cuando se busca un producto que no existe.
    
    Esta excepción representa un error de negocio donde se intenta
    acceder a un producto que no está en el repositorio.
    """
    
    def __init__(self, product_id: Optional[int] = None):
        """
        Inicializa la excepción ProductNotFoundError.
        
        Args:
            product_id: El ID del producto no encontrado (opcional).
                       Si se proporciona, se incluye en el mensaje.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        
        super().__init__(self.message)

class InvalidProductDataError(Exception):
    """
    Se lanza cuando los datos de un producto son inválidos.
    
    Esta excepción representa un error de negocio donde los datos
    del producto no cumplen con las reglas de validación del dominio.
    """
    
    def __init__(self, message: str = "Datos de producto inválidos"):
        """
        Inicializa la excepción InvalidProductDataError.
        
        Args:
            message: Mensaje personalizado describiendo qué datos son inválidos.
                    Por defecto: "Datos de producto inválidos"
        """
        self.message = message
        super().__init__(self.message)

class ChatServiceError(Exception):
    """
    Se lanza cuando hay un error en el servicio de chat.
    
    Esta excepción representa un error de negocio en las operaciones
    relacionadas con el servicio de chat.
    """
    
    def __init__(self, message: str = "Error en el servicio de chat"):
        """
        Inicializa la excepción ChatServiceError.
        
        Args:
            message: Mensaje personalizado describiendo el error.
                    Por defecto: "Error en el servicio de chat"
        """
        self.message = message
        super().__init__(self.message)

class InsufficientStockError(Exception):
    """
    Se lanza cuando no hay suficiente stock de un producto.
    
    Esta excepción representa un error de negocio donde se intenta
    realizar una transacción pero el stock disponible es insuficiente.
    """
    
    def __init__(
        self,
        product_id: int,
        available_stock: int,
        requested_quantity: int
    ):
        """
        Inicializa la excepción InsufficientStockError.
        
        Args:
            product_id: El ID del producto con stock insuficiente.
            available_stock: Cantidad de stock disponible.
            requested_quantity: Cantidad solicitada.
        """
        self.message = (
            f"Stock insuficiente para el producto ID {product_id}. "
            f"Disponible: {available_stock}, Solicitado: {requested_quantity}"
        )
        super().__init__(self.message)

class InvalidSessionError(Exception):
    """
    Se lanza cuando se intenta acceder a una sesión de chat inválida.
    
    Esta excepción representa un error de negocio donde la sesión
    no existe o no es válida.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa la excepción InvalidSessionError.
        
        Args:
            session_id: El ID de la sesión inválida (opcional).
                       Si se proporciona, se incluye en el mensaje.
        """
        if session_id:
            self.message = f"Sesión con ID '{session_id}' inválida o no encontrada"
        else:
            self.message = "Sesión inválida o no encontrada"
        
        super().__init__(self.message)