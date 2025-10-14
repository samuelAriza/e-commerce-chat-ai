from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage

class IProductRepository(ABC):
    """
    Interface que define el contrato para acceder a productos.
    Las implementaciones concretas estarán en la capa de infraestructura.
    """
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        TODO: Define el método para obtener todos los productos
        No implementes nada, solo la firma del método
        """
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        TODO: Define el método para obtener un producto por ID
        Retorna None si no existe
        """
        pass
    
    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """TODO: Obtiene productos de una marca específica"""
        pass
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """TODO: Obtiene productos de una categoría específica"""
        pass
    
    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        TODO: Guarda o actualiza un producto
        Si tiene ID, actualiza. Si no tiene ID, crea uno nuevo
        Retorna el producto guardado (con ID asignado si es nuevo)
        """
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        TODO: Elimina un producto por ID
        Retorna True si se eliminó, False si no existía
        """
        pass

class IChatRepository(ABC):
    """
    Interface para gestionar el historial de conversaciones.
    """
    
    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        TODO: Guarda un mensaje en el historial
        Retorna el mensaje guardado con su ID
        """
        pass
    
    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        TODO: Obtiene el historial completo de una sesión
        Si limit está definido, retorna solo los últimos N mensajes
        Los mensajes deben estar en orden cronológico (más antiguos primero)
        """
        pass
    
    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        TODO: Elimina todo el historial de una sesión
        Retorna la cantidad de mensajes eliminados
        """
        pass
    
    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        TODO: Obtiene los últimos N mensajes de una sesión
        Crucial para mantener el contexto conversacional
        Retorna en orden cronológico
        """
        pass