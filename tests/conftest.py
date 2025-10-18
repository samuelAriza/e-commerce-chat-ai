"""
Configuración global de fixtures para tests.

Este módulo contiene fixtures compartidos que pueden ser utilizados
por todos los tests de la aplicación. Incluye configuración de base
de datos de prueba, cliente HTTP y datos de ejemplo.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from src.infrastructure.db.database import Base
from src.infrastructure.api.main import app


@pytest.fixture(scope="function")
def test_db():
    """
    Crea una base de datos SQLite en memoria para tests.
    
    Esta fixture se recrea para cada función de test (scope=function)
    para garantizar aislamiento entre tests. Crea todas las tablas
    necesarias y las elimina al finalizar el test.
    
    Yields:
        Session: Sesión de SQLAlchemy para el test.
    """
    # Crear engine en memoria
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Crear sesión
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session):
    """
    Crea un cliente de prueba de FastAPI.
    
    Este cliente utiliza la base de datos de prueba en lugar
    de la base de datos real, permitiendo tests aislados de la API.
    
    Args:
        test_db: Sesión de base de datos de prueba.
        
    Yields:
        TestClient: Cliente HTTP para hacer requests a la API.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    from src.infrastructure.db.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """
    Proporciona datos de ejemplo para un producto.
    
    Returns:
        dict: Diccionario con datos válidos de un producto.
    """
    return {
        "name": "Nike Air Max Test",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Negro",
        "price": 129.99,
        "stock": 10,
        "description": "Zapatillas de prueba"
    }


@pytest.fixture
def sample_chat_message():
    """
    Proporciona datos de ejemplo para un mensaje de chat.
    
    Returns:
        dict: Diccionario con datos válidos de un mensaje de chat.
    """
    return {
        "session_id": "test_session_123",
        "message": "¿Qué zapatillas tienen disponibles?"
    }