"""
Tests unitarios para las entidades del dominio.

Prueba las validaciones y métodos de negocio de Product, ChatMessage
y ChatContext sin dependencias externas.
"""
import pytest
from datetime import datetime

from src.domain.entities import Product, ChatMessage, ChatContext

class TestProduct:
    """Tests para la entidad Product."""
    
    def test_product_creation_valid(self):
        """
        Verifica que se puede crear un producto con datos válidos.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Zapatillas deportivas"
        )
        
        assert product.name == "Nike Air Max"
        assert product.price == 129.99
        assert product.stock == 10
    
    def test_product_validation_empty_name(self):
        """
        Verifica que lanza ValueError si el nombre está vacío.
        """
        with pytest.raises(ValueError, match="nombre.*no puede estar vacío"):
            Product(
                id=1,
                name="",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=129.99,
                stock=10,
                description="Test"
            )
    
    def test_product_validation_negative_price(self):
        """
        Verifica que lanza ValueError si el precio es negativo o cero.
        """
        with pytest.raises(ValueError, match="precio.*mayor a 0"):
            Product(
                id=1,
                name="Nike Air Max",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=-10.0,
                stock=10,
                description="Test"
            )
    
    def test_product_validation_negative_stock(self):
        """
        Verifica que lanza ValueError si el stock es negativo.
        """
        with pytest.raises(ValueError, match="stock.*no puede ser negativo"):
            Product(
                id=1,
                name="Nike Air Max",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=129.99,
                stock=-5,
                description="Test"
            )
    
    def test_is_available_with_stock(self):
        """
        Verifica que is_available() retorna True cuando hay stock.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        assert product.is_available() is True
    
    def test_is_available_without_stock(self):
        """
        Verifica que is_available() retorna False cuando no hay stock.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=0,
            description="Test"
        )
        
        assert product.is_available() is False
    
    def test_reduce_stock_valid(self):
        """
        Verifica que reduce_stock() reduce correctamente el inventario.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        product.reduce_stock(3)
        assert product.stock == 7
    
    def test_reduce_stock_insufficient(self):
        """
        Verifica que reduce_stock() lanza ValueError si no hay suficiente stock.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=5,
            description="Test"
        )
        
        with pytest.raises(ValueError, match="No hay suficiente stock"):
            product.reduce_stock(10)
    
    def test_reduce_stock_negative_quantity(self):
        """
        Verifica que reduce_stock() lanza ValueError con cantidad negativa.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        with pytest.raises(ValueError, match="cantidad.*debe ser positiva"):
            product.reduce_stock(-5)
    
    def test_increase_stock_valid(self):
        """
        Verifica que increase_stock() aumenta correctamente el inventario.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        product.increase_stock(5)
        assert product.stock == 15
    
    def test_increase_stock_negative_quantity(self):
        """
        Verifica que increase_stock() lanza ValueError con cantidad negativa.
        """
        product = Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        with pytest.raises(ValueError, match="cantidad.*debe ser positiva"):
            product.increase_stock(-3)


class TestChatMessage:
    """Tests para la entidad ChatMessage."""
    
    def test_chat_message_creation_valid(self):
        """
        Verifica que se puede crear un mensaje de chat con datos válidos.
        """
        message = ChatMessage(
            id=1,
            session_id="session_123",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow()
        )
        
        assert message.session_id == "session_123"
        assert message.role == "user"
        assert message.message == "Hola"
    
    def test_chat_message_validation_invalid_role(self):
        """
        Verifica que lanza ValueError si el role no es 'user' o 'assistant'.
        """
        with pytest.raises(ValueError, match="role debe ser 'user' o 'assistant'"):
            ChatMessage(
                id=1,
                session_id="session_123",
                role="invalid_role",
                message="Hola",
                timestamp=datetime.utcnow()
            )
    
    def test_chat_message_validation_empty_message(self):
        """
        Verifica que lanza ValueError si el mensaje está vacío.
        """
        with pytest.raises(ValueError, match="mensaje no puede estar vacío"):
            ChatMessage(
                id=1,
                session_id="session_123",
                role="user",
                message="",
                timestamp=datetime.utcnow()
            )
    
    def test_chat_message_validation_empty_session_id(self):
        """
        Verifica que lanza ValueError si el session_id está vacío.
        """
        with pytest.raises(ValueError, match="session_id.*no puede estar vacío"):
            ChatMessage(
                id=1,
                session_id="",
                role="user",
                message="Hola",
                timestamp=datetime.utcnow()
            )
    
    def test_is_from_user(self):
        """
        Verifica que is_from_user() retorna True para mensajes de usuario.
        """
        message = ChatMessage(
            id=1,
            session_id="session_123",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow()
        )
        
        assert message.is_from_user() is True
        assert message.is_from_assistant() is False
    
    def test_is_from_assistant(self):
        """
        Verifica que is_from_assistant() retorna True para mensajes del asistente.
        """
        message = ChatMessage(
            id=1,
            session_id="session_123",
            role="assistant",
            message="Hola, ¿en qué puedo ayudarte?",
            timestamp=datetime.utcnow()
        )
        
        assert message.is_from_assistant() is True
        assert message.is_from_user() is False


class TestChatContext:
    """Tests para el value object ChatContext."""
    
    def test_get_recent_messages_less_than_max(self):
        """
        Verifica que get_recent_messages() retorna todos los mensajes
        si hay menos que max_messages.
        """
        messages = [
            ChatMessage(
                id=i,
                session_id="session_123",
                role="user" if i % 2 == 0 else "assistant",
                message=f"Mensaje {i}",
                timestamp=datetime.utcnow()
            )
            for i in range(3)
        ]
        
        context = ChatContext(messages=messages, max_messages=6)
        recent = context.get_recent_messages()
        
        assert len(recent) == 3
    
    def test_get_recent_messages_more_than_max(self):
        """
        Verifica que get_recent_messages() retorna solo los últimos
        max_messages mensajes.
        """
        messages = [
            ChatMessage(
                id=i,
                session_id="session_123",
                role="user" if i % 2 == 0 else "assistant",
                message=f"Mensaje {i}",
                timestamp=datetime.utcnow()
            )
            for i in range(10)
        ]
        
        context = ChatContext(messages=messages, max_messages=6)
        recent = context.get_recent_messages()
        
        assert len(recent) == 6
        assert recent[0].id == 4  # Los últimos 6 mensajes (4, 5, 6, 7, 8, 9)
    
    def test_format_for_prompt(self):
        """
        Verifica que format_for_prompt() formatea correctamente los mensajes.
        """
        messages = [
            ChatMessage(
                id=1,
                session_id="session_123",
                role="user",
                message="Hola",
                timestamp=datetime.utcnow()
            ),
            ChatMessage(
                id=2,
                session_id="session_123",
                role="assistant",
                message="Hola, ¿en qué puedo ayudarte?",
                timestamp=datetime.utcnow()
            )
        ]
        
        context = ChatContext(messages=messages, max_messages=6)
        formatted = context.format_for_prompt()
        
        assert "Usuario: Hola" in formatted
        assert "Asistente: Hola, ¿en qué puedo ayudarte?" in formatted
    
    def test_format_for_prompt_empty(self):
        """
        Verifica que format_for_prompt() maneja lista vacía correctamente.
        """
        context = ChatContext(messages=[], max_messages=6)
        formatted = context.format_for_prompt()
        
        assert formatted == ""