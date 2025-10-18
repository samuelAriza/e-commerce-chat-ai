"""
Tests unitarios para los servicios de aplicación.

Prueba ProductService y ChatService usando mocks de repositorios
para aislar la lógica de negocio de la infraestructura.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from src.domain.entities import Product, ChatMessage
from src.domain.exceptions import (
    ProductNotFoundError,
    InvalidProductDataError,
    ChatServiceError,
    InvalidSessionError
)

class TestProductService:
    """Tests para ProductService."""
    
    @pytest.fixture
    def mock_repository(self):
        """
        Crea un mock del repositorio de productos.
        
        Returns:
            Mock: Repositorio mockeado con métodos simulados.
        """
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """
        Crea una instancia de ProductService con repositorio mock.
        
        Args:
            mock_repository: Repositorio mockeado.
            
        Returns:
            ProductService: Servicio con dependencias mockeadas.
        """
        return ProductService(repository=mock_repository)
    
    @pytest.fixture
    def sample_product(self):
        """
        Crea un producto de ejemplo.
        
        Returns:
            Product: Producto de prueba.
        """
        return Product(
            id=1,
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Zapatillas de prueba"
        )
    
    def test_get_all_products(self, service, mock_repository, sample_product):
        """
        Verifica que get_all_products() retorna todos los productos.
        """
        # Configurar mock
        mock_repository.get_all.return_value = [sample_product]
        
        # Ejecutar
        products = service.get_all_products()
        
        # Verificar
        assert len(products) == 1
        assert products[0].name == "Nike Air Max"
        mock_repository.get_all.assert_called_once()
    
    def test_get_product_by_id_exists(self, service, mock_repository, sample_product):
        """
        Verifica que get_product_by_id() retorna el producto si existe.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = sample_product
        
        # Ejecutar
        product = service.get_product_by_id(1)
        
        # Verificar
        assert product.id == 1
        assert product.name == "Nike Air Max"
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_product_by_id_not_exists(self, service, mock_repository):
        """
        Verifica que get_product_by_id() lanza ProductNotFoundError
        si el producto no existe.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = None
        
        # Verificar excepción
        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(999)
        
        mock_repository.get_by_id.assert_called_once_with(999)
    
    def test_create_product_valid(self, service, mock_repository, sample_product):
        """
        Verifica que create_product() crea un producto correctamente.
        """
        # Configurar mock
        mock_repository.save.return_value = sample_product
        
        # Crear DTO
        product_dto = ProductDTO(
            name="Nike Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Zapatillas de prueba"
        )
        
        # Ejecutar
        created = service.create_product(product_dto)
        
        # Verificar
        assert created.name == "Nike Air Max"
        mock_repository.save.assert_called_once()
    
    def test_create_product_invalid_data(self, service, mock_repository):
        """
        Verifica que create_product() lanza InvalidProductDataError
        con datos inválidos.
        """
        # Configurar mock para lanzar excepción
        mock_repository.save.side_effect = ValueError("Precio inválido")
        
        # Crear DTO con datos inválidos
        product_dto = ProductDTO(
            name="Test",
            brand="Test",
            category="Test",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        # Verificar excepción
        with pytest.raises(InvalidProductDataError):
            service.create_product(product_dto)
    
    def test_update_product_exists(self, service, mock_repository, sample_product):
        """
        Verifica que update_product() actualiza un producto existente.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = sample_product
        mock_repository.save.return_value = sample_product
        
        # Crear DTO con cambios
        product_dto = ProductDTO(
            id=1,
            name="Nike Air Max Updated",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=139.99,
            stock=15,
            description="Actualizado"
        )
        
        # Ejecutar
        updated = service.update_product(1, product_dto)
        
        # Verificar
        assert updated is not None
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()
    
    def test_update_product_not_exists(self, service, mock_repository):
        """
        Verifica que update_product() lanza ProductNotFoundError
        si el producto no existe.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = None
        
        # Crear DTO
        product_dto = ProductDTO(
            id=999,
            name="Test",
            brand="Test",
            category="Test",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        
        # Verificar excepción
        with pytest.raises(ProductNotFoundError):
            service.update_product(999, product_dto)
    
    def test_delete_product_exists(self, service, mock_repository, sample_product):
        """
        Verifica que delete_product() elimina un producto existente.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = sample_product
        mock_repository.delete.return_value = True
        
        # Ejecutar
        result = service.delete_product(1)
        
        # Verificar
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_product_not_exists(self, service, mock_repository):
        """
        Verifica que delete_product() lanza ProductNotFoundError
        si el producto no existe.
        """
        # Configurar mock
        mock_repository.get_by_id.return_value = None
        
        # Verificar excepción
        with pytest.raises(ProductNotFoundError):
            service.delete_product(999)
    
    def test_get_available_products(self, service, mock_repository):
        """
        Verifica que get_available_products() retorna solo productos con stock.
        """
        # Crear productos de prueba
        product_with_stock = Product(
            id=1,
            name="Product 1",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Con stock"
        )
        
        product_without_stock = Product(
            id=2,
            name="Product 2",
            brand="Adidas",
            category="Running",
            size="42",
            color="Blanco",
            price=99.99,
            stock=0,
            description="Sin stock"
        )
        
        # Configurar mock
        mock_repository.get_all.return_value = [product_with_stock, product_without_stock]
        
        # Ejecutar
        available = service.get_available_products()
        
        # Verificar
        assert len(available) == 1
        assert available[0].stock > 0
    
    def test_search_products_by_brand(self, service, mock_repository, sample_product):
        """
        Verifica que search_products() filtra por marca correctamente.
        """
        # Configurar mock
        mock_repository.get_by_brand.return_value = [sample_product]
        
        # Ejecutar
        products = service.search_products({"brand": "Nike"})
        
        # Verificar
        assert len(products) == 1
        assert products[0].brand == "Nike"
        mock_repository.get_by_brand.assert_called_once_with("Nike")


class TestChatService:
    """Tests para ChatService."""
    
    @pytest.fixture
    def mock_product_repository(self):
        """Crea un mock del repositorio de productos."""
        return Mock()
    
    @pytest.fixture
    def mock_chat_repository(self):
        """Crea un mock del repositorio de chat."""
        return Mock()
    
    @pytest.fixture
    def mock_ai_service(self):
        """Crea un mock del servicio de IA."""
        mock = Mock()
        mock.generate_response = AsyncMock(return_value="Respuesta de prueba")
        return mock
    
    @pytest.fixture
    def service(self, mock_product_repository, mock_chat_repository, mock_ai_service):
        """Crea una instancia de ChatService con mocks."""
        return ChatService(
            product_repository=mock_product_repository,
            chat_repository=mock_chat_repository,
            ai_service=mock_ai_service
        )
    
    @pytest.mark.asyncio
    async def test_process_message_valid(
        self,
        service,
        mock_product_repository,
        mock_chat_repository,
        mock_ai_service
    ):
        """
        Verifica que process_message() procesa un mensaje correctamente.
        """
        # Configurar mocks
        mock_product_repository.get_all.return_value = []
        mock_chat_repository.get_recent_messages.return_value = []
        
        # Simular guardado de mensajes
        def save_message_side_effect(msg):
            msg.id = 1
            return msg
        
        mock_chat_repository.save_message.side_effect = save_message_side_effect
        
        # Crear request
        request = ChatMessageRequestDTO(
            session_id="test_session",
            message="Hola"
        )
        
        # Ejecutar
        response = await service.process_message(request)
        
        # Verificar
        assert response.session_id == "test_session"
        assert response.user_message == "Hola"
        assert response.assistant_message == "Respuesta de prueba"
        assert mock_chat_repository.save_message.call_count == 2  # Usuario + Asistente
    
    @pytest.mark.asyncio
    async def test_get_session_history(
        self,
        service,
        mock_chat_repository
    ):
        """
        Verifica que get_session_history() retorna el historial correctamente.
        """
        # Configurar mock
        messages = [
            ChatMessage(
                id=1,
                session_id="test_session",
                role="user",
                message="Hola",
                timestamp=datetime.utcnow()
            )
        ]
        mock_chat_repository.get_session_history.return_value = messages
        
        # Ejecutar
        history = await service.get_session_history("test_session", limit=10)
        
        # Verificar
        assert len(history) == 1
        assert history[0].message == "Hola"
    
    @pytest.mark.asyncio
    async def test_clear_session_history(
        self,
        service,
        mock_chat_repository
    ):
        """
        Verifica que clear_session_history() elimina el historial correctamente.
        """
        # Configurar mock
        mock_chat_repository.delete_session_history.return_value = 5
        
        # Ejecutar
        deleted_count = await service.clear_session_history("test_session")
        
        # Verificar
        assert deleted_count == 5
        mock_chat_repository.delete_session_history.assert_called_once_with(session_id="test_session")

    
    @pytest.mark.asyncio
    async def test_clear_session_history_invalid_session(self, service):
        """
        Verifica que clear_session_history() lanza InvalidSessionError
        con session_id vacío.
        """
        # Verificar excepción
        with pytest.raises(InvalidSessionError):
            await service.clear_session_history("")
    
    @pytest.mark.asyncio
    async def test_process_message_with_context(
        self,
        service,
        mock_product_repository,
        mock_chat_repository,
        mock_ai_service
    ):
        """
        Verifica que process_message() incluye contexto conversacional.
        """
        # Configurar productos
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
        mock_product_repository.get_all.return_value = [product]
        
        # Configurar historial previo
        previous_messages = [
            ChatMessage(
                id=1,
                session_id="test_session",
                role="user",
                message="Hola",
                timestamp=datetime.utcnow()
            ),
            ChatMessage(
                id=2,
                session_id="test_session",
                role="assistant",
                message="Hola, ¿en qué puedo ayudarte?",
                timestamp=datetime.utcnow()
            )
        ]
        mock_chat_repository.get_recent_messages.return_value = previous_messages
        
        # Simular guardado de mensajes
        def save_message_side_effect(msg):
            msg.id = len(previous_messages) + 1
            return msg
        
        mock_chat_repository.save_message.side_effect = save_message_side_effect
        
        # Crear request
        request = ChatMessageRequestDTO(
            session_id="test_session",
            message="¿Qué zapatillas tienen?"
        )
        
        # Ejecutar
        response = await service.process_message(request)
        
        # Verificar que se llamó a generate_response con contexto
        assert mock_ai_service.generate_response.called
        call_args = mock_ai_service.generate_response.call_args
        assert "conversation_context" in call_args.kwargs
        assert "products_info" in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_get_recent_context(
        self,
        service,
        mock_chat_repository
    ):
        """
        Verifica que get_recent_context() retorna el contexto correctamente.
        """
        # Configurar mock
        messages = [
            ChatMessage(
                id=i,
                session_id="test_session",
                role="user" if i % 2 == 0 else "assistant",
                message=f"Mensaje {i}",
                timestamp=datetime.utcnow()
            )
            for i in range(6)
        ]
        mock_chat_repository.get_recent_messages.return_value = messages
        
        # Ejecutar
        context = await service.get_recent_context("test_session", count=6)
        
        # Verificar
        assert len(context.messages) == 6
        mock_chat_repository.get_recent_messages.assert_called_once_with(
            session_id="test_session",
            count=6
        )


class TestProductServiceEdgeCases:
    """Tests de casos extremos para ProductService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Crea un mock del repositorio de productos."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Crea una instancia de ProductService con repositorio mock."""
        return ProductService(repository=mock_repository)
    
    def test_get_all_products_empty(self, service, mock_repository):
        """
        Verifica que get_all_products() maneja correctamente lista vacía.
        """
        # Configurar mock
        mock_repository.get_all.return_value = []
        
        # Ejecutar
        products = service.get_all_products()
        
        # Verificar
        assert products == []
        assert isinstance(products, list)
    
    def test_search_products_no_filters(self, service, mock_repository):
        """
        Verifica que search_products() sin filtros retorna todos los productos.
        """
        # Configurar mock
        product = Product(
            id=1,
            name="Test",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=10,
            description="Test"
        )
        mock_repository.get_all.return_value = [product]
        
        # Ejecutar
        products = service.search_products({})
        
        # Verificar
        assert len(products) == 1
    
    def test_reduce_product_stock_to_zero(self, service, mock_repository):
        """
        Verifica que reduce_product_stock() puede reducir stock a cero.
        """
        # Crear producto con stock
        product = Product(
            id=1,
            name="Test",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=5,
            description="Test"
        )
        
        # Configurar mock
        mock_repository.get_by_id.return_value = product
        mock_repository.save.return_value = product
        
        # Ejecutar
        updated = service.reduce_product_stock(1, 5)
        
        # Verificar
        assert updated.stock == 0
        assert not updated.is_available
    
    def test_increase_product_stock_from_zero(self, service, mock_repository):
        """
        Verifica que increase_product_stock() puede aumentar desde cero.
        """
        # Crear producto sin stock
        product = Product(
            id=1,
            name="Test",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=129.99,
            stock=0,
            description="Test"
        )
        
        # Configurar mock
        mock_repository.get_by_id.return_value = product
        mock_repository.save.return_value = product
        
        # Ejecutar
        updated = service.increase_product_stock(1, 10)
        
        # Verificar
        assert updated.stock == 10
        assert updated.is_available


class TestChatServiceEdgeCases:
    """Tests de casos extremos para ChatService."""
    
    @pytest.fixture
    def mock_product_repository(self):
        """Crea un mock del repositorio de productos."""
        return Mock()
    
    @pytest.fixture
    def mock_chat_repository(self):
        """Crea un mock del repositorio de chat."""
        return Mock()
    
    @pytest.fixture
    def mock_ai_service(self):
        """Crea un mock del servicio de IA."""
        mock = Mock()
        mock.generate_response = AsyncMock(return_value="Respuesta de prueba")
        return mock
    
    @pytest.fixture
    def service(self, mock_product_repository, mock_chat_repository, mock_ai_service):
        """Crea una instancia de ChatService con mocks."""
        return ChatService(
            product_repository=mock_product_repository,
            chat_repository=mock_chat_repository,
            ai_service=mock_ai_service
        )
    
    @pytest.mark.asyncio
    async def test_process_message_no_products(
        self,
        service,
        mock_product_repository,
        mock_chat_repository
    ):
        """
        Verifica que process_message() funciona sin productos disponibles.
        """
        # Configurar mocks
        mock_product_repository.get_all.return_value = []
        mock_chat_repository.get_recent_messages.return_value = []
        
        # Simular guardado
        def save_message_side_effect(msg):
            msg.id = 1
            return msg
        
        mock_chat_repository.save_message.side_effect = save_message_side_effect
        
        # Crear request
        request = ChatMessageRequestDTO(
            session_id="test_session",
            message="Hola"
        )
        
        # Ejecutar
        response = await service.process_message(request)
        
        # Verificar
        assert response is not None
        assert response.assistant_message == "Respuesta de prueba"
    
    @pytest.mark.asyncio
    async def test_get_session_history_empty(
        self,
        service,
        mock_chat_repository
    ):
        """
        Verifica que get_session_history() maneja historial vacío.
        """
        # Configurar mock
        mock_chat_repository.get_session_history.return_value = []
        
        # Ejecutar
        history = await service.get_session_history("test_session")
        
        # Verificar
        assert history == []
        assert isinstance(history, list)
    
    @pytest.mark.asyncio
    async def test_clear_session_history_no_messages(
        self,
        service,
        mock_chat_repository
    ):
        """
        Verifica que clear_session_history() retorna 0 si no hay mensajes.
        """
        # Configurar mock
        mock_chat_repository.delete_session_history.return_value = 0
        
        # Ejecutar
        deleted_count = await service.clear_session_history("test_session")
        
        # Verificar
        assert deleted_count == 0