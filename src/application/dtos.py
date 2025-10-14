from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ProductDTO(BaseModel):
    """
    DTO (Data Transfer Object) para transferir datos de productos.
    
    Utiliza Pydantic para validación automática de tipos y valores.
    Permite transferir datos entre capas de forma segura.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        """
        Valida que el precio sea mayor a 0.
        
        Args:
            v: El valor del precio a validar.
            
        Raises:
            ValueError: Si el precio es menor o igual a 0.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v
    
    @field_validator('stock')
    @classmethod
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock no sea negativo.
        
        Args:
            v: El valor del stock a validar.
            
        Raises:
            ValueError: Si el stock es negativo.
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v
    
    class Config:
        """Configuración de Pydantic"""
        from_attributes = True  # Permite crear DTOs desde objetos ORM


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario.
    
    Valida que los datos del mensaje sean correctos antes de procesarlos
    en la capa de aplicación.
    """
    session_id: str
    message: str
    
    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v):
        """
        Valida que el mensaje no esté vacío.
        
        Args:
            v: El valor del mensaje a validar.
            
        Raises:
            ValueError: Si el mensaje está vacío o solo contiene espacios.
        """
        if not v or v.strip() == "":
            raise ValueError("El mensaje no puede estar vacío")
        return v
    
    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v):
        """
        Valida que session_id no esté vacío.
        
        Args:
            v: El valor del session_id a validar.
            
        Raises:
            ValueError: Si session_id está vacío o solo contiene espacios.
        """
        if not v or v.strip() == "":
            raise ValueError("El session_id no puede estar vacío")
        return v


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para enviar respuestas del chat.
    
    Encapsula la respuesta completa del servicio de chat,
    incluyendo el mensaje del usuario y la respuesta del asistente.
    """
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para mostrar historial de chat.
    
    Representa un mensaje individual del historial conversacional.
    Permite serializar mensajes del dominio para enviarlos a través de la API.
    """
    id: int
    role: str
    message: str
    timestamp: datetime
    
    class Config:
        """Configuración de Pydantic"""
        from_attributes = True