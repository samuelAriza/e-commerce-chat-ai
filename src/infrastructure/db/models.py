from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class ProductModel(Base):
    """
    Modelo ORM que representa un producto en la base de datos.
    
    Mapea la tabla 'products' con todos los atributos de un producto
    del e-commerce (nombre, marca, categoría, precio, stock, etc.).
    """
    
    __tablename__ = "products"
    
    # Clave primaria
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Identificador único del producto"
    )
    
    # Información del producto
    name = Column(
        String(200),
        nullable=False,
        index=True,
        doc="Nombre del producto"
    )
    
    brand = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Marca del producto"
    )
    
    category = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Categoría del producto"
    )
    
    size = Column(
        String(20),
        nullable=False,
        doc="Talla o tamaño del producto"
    )
    
    color = Column(
        String(50),
        nullable=False,
        doc="Color del producto"
    )
    
    # Información económica
    price = Column(
        Float,
        nullable=False,
        doc="Precio del producto en moneda local"
    )
    
    stock = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Cantidad disponible en stock"
    )
    
    # Descripción
    description = Column(
        Text,
        nullable=True,
        doc="Descripción detallada del producto"
    )
    
    def __repr__(self) -> str:
        """Representación en string del modelo para debugging."""
        return (
            f"<ProductModel(id={self.id}, name='{self.name}', "
            f"brand='{self.brand}', price={self.price}, stock={self.stock})>"
        )


class ChatMemoryModel(Base):
    """
    Modelo ORM que representa un mensaje en el historial de chat.
    
    Mapea la tabla 'chat_memory' con todos los mensajes de conversaciones.
    Incluye información sobre la sesión, el rol del emisor y el timestamp
    para mantener el historial conversacional ordenado cronológicamente.
    """
    
    __tablename__ = "chat_memory"
    
    # Clave primaria
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Identificador único del mensaje"
    )
    
    # Identificación de sesión
    session_id = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Identificador único de la sesión de chat"
    )
    
    # Rol del emisor
    role = Column(
        String(20),
        nullable=False,
        doc="Rol del emisor: 'user' o 'assistant'"
    )
    
    # Contenido del mensaje
    message = Column(
        Text,
        nullable=False,
        doc="Contenido del mensaje en la conversación"
    )
    
    # Marca de tiempo
    timestamp = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        doc="Fecha y hora UTC cuando se creó el mensaje"
    )
    
    def __repr__(self) -> str:
        """Representación en string del modelo para debugging."""
        return (
            f"<ChatMemoryModel(id={self.id}, session_id='{self.session_id}', "
            f"role='{self.role}', timestamp='{self.timestamp}')>"
        )


# Indices compuestos para optimizar busquedas frecuentes
# Estos se crean automáticamente cuando se ejecuta init_db()

# Indice para buscar mensajes de una sesión ordenados por timestamp
chat_session_timestamp_index = Index(
    'idx_chat_session_timestamp',
    ChatMemoryModel.session_id,
    ChatMemoryModel.timestamp,
    info={"description": "Índice para búsquedas rápidas de mensajes por sesión ordenados por fecha"}
)

# Indice para búsquedas por marca y categoría en productos
product_brand_category_index = Index(
    'idx_product_brand_category',
    ProductModel.brand,
    ProductModel.category,
    info={"description": "Índice para filtrados rápidos por marca y categoría"}
)