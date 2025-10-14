from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """
    Entidad que representa un producto en el e-commerce.
    Contiene la lógica de negocio relacionada con productos.
    """
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self):
        """
        Validaciones que se ejecutan después de crear el objeto.
        
        Realiza las siguientes validaciones:
        - El precio debe ser mayor a 0
        - El stock no puede ser negativo
        - El nombre no puede estar vacío
        
        Levanta ValueError si alguna validación falla.
        """
        # Valida que el nombre no esté vacío
        if not self.name or self.name.strip() == "":
            raise ValueError("El nombre del producto no puede estar vacío")
        
        # Valida que el precio sea mayor a 0
        if self.price <= 0:
            raise ValueError("El precio del producto debe ser mayor a 0")
        
        # Valida que el stock no sea negativo
        if self.stock < 0:
            raise ValueError("El stock del producto no puede ser negativo")

    def is_available(self) -> bool:
        """
        Verifica si el producto tiene stock disponible.
        
        Retorna:
            bool: True si hay stock disponible (stock > 0), False en caso contrario
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.
        
        Realiza las siguientes validaciones:
        - Valida que la cantidad sea positiva (mayor a 0)
        - Valida que haya suficiente stock disponible
        
        Levanta ValueError si no se puede reducir el stock.
        
        Args:
            quantity: La cantidad a reducir del stock (debe ser positiva)
            
        Raises:
            ValueError: Si la cantidad es menor o igual a 0
            ValueError: Si no hay suficiente stock para reducir
        """
        # Valida que la cantidad sea positiva
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        
        # Valida que haya suficiente stock
        if quantity > self.stock:
            raise ValueError(
                f"No hay suficiente stock. Stock disponible: {self.stock}, "
                f"cantidad solicitada: {quantity}"
            )
        
        # Reduce el stock
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto en la cantidad especificada.
        
        Realiza la siguiente validación:
        - Valida que la cantidad sea positiva (mayor a 0)
        
        Levanta ValueError si no se puede aumentar el stock.
        
        Args:
            quantity: La cantidad a aumentar del stock (debe ser positiva)
            
        Raises:
            ValueError: Si la cantidad es menor o igual a 0
        """
        # Valida que la cantidad sea positiva
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        
        # Aumenta el stock
        self.stock += quantity

@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en el chat.
    Contiene la lógica de validación y verificación de mensajes.
    """
    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime
    
    def __post_init__(self):
        """
        Validaciones que se ejecutan después de crear el objeto.
        
        Realiza las siguientes validaciones:
        - El role debe ser 'user' o 'assistant'
        - El message no puede estar vacío
        - El session_id no puede estar vacío
        
        Levanta ValueError si alguna validación falla.
        """
        # Valida que session_id no esté vacío
        if not self.session_id or self.session_id.strip() == "":
            raise ValueError("El session_id del mensaje no puede estar vacío")
        
        # Valida que el role sea válido
        if self.role not in ['user', 'assistant']:
            raise ValueError(
                f"El role debe ser 'user' o 'assistant', se recibió: {self.role}"
            )
        
        # Valida que el message no esté vacío
        if not self.message or self.message.strip() == "":
            raise ValueError("El mensaje no puede estar vacío")
    
    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje es del usuario.
        
        Retorna:
            bool: True si el role es 'user', False en caso contrario
        """
        return self.role == 'user'
    
    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje es del asistente.
        
        Retorna:
            bool: True si el role es 'assistant', False en caso contrario
        """
        return self.role == 'assistant'

@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.
    Mantiene los mensajes recientes para dar coherencia al chat.
    """
    messages: list[ChatMessage]
    max_messages: int = 6
    
    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Retorna los últimos N mensajes según max_messages.
        
        Utiliza slicing de Python para obtener los últimos mensajes
        del historial. Si hay menos mensajes que max_messages, retorna
        todos los disponibles.
        
        Retorna:
            list[ChatMessage]: Lista con los últimos N mensajes (máximo max_messages)
        """
        return self.messages[-self.max_messages:]
    
    def format_for_prompt(self) -> str:
        """
        Formatea los mensajes recientes para incluirlos en el prompt de la IA.
        
        Crea un string con el historial conversacional en el siguiente formato:
        "Usuario: mensaje del usuario
        Asistente: respuesta del asistente
        Usuario: otro mensaje
        ..."
        
        Esto permite que la IA tenga contexto de la conversación anterior.
        
        Retorna:
            str: String formateado con el historial conversacional
        """
        # Obtiene los mensajes recientes
        recent_messages = self.get_recent_messages()
        
        # Construye el string formateado
        formatted_lines = []
        
        for chat_message in recent_messages:
            # Determina el prefijo según el role
            if chat_message.role == 'user':
                prefix = "Usuario"
            else:
                prefix = "Asistente"
            
            # Agrega el mensaje formateado a la lista
            formatted_lines.append(f"{prefix}: {chat_message.message}")
        
        # Une todos los mensajes con saltos de línea
        return "\n".join(formatted_lines)