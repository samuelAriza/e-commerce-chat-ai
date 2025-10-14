from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from dotenv import load_dotenv  

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la URL de la base de datos SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear directorio de datos si no existe
os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///./", "")), exist_ok=True)

# Crear el motor de SQLAlchemy
# check_same_thread=False permite usar la BD desde múltiples threads (necesario para FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Pool de conexiones estático para SQLite
    echo=False  # Cambiar a True para ver las queries SQL en consola
)

# Crear factory de sesiones
# expire_on_commit=False permite acceder a atributos después de hacer commit
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Clase base para todos los modelos ORM
# Los modelos heredarán de esta clase
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency provider para FastAPI.
    
    Proporciona una sesión de BD para cada request.
    Usa yield para asegurar que la sesión se cierre después del request,
    incluso si hay excepciones.
    
    Yield:
        Session: Sesión de SQLAlchemy para usar en el endpoint.
        
    Ejemplo de uso en FastAPI:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            products = db.query(ProductModel).all()
            return products
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Siempre se ejecuta, incluso si hay excepción
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    
    - Crea todas las tablas definidas en los modelos ORM
    - Debe llamarse al inicio de la aplicación (en main.py)
    - Si las tablas ya existen, no hace nada
    
    Ejemplo:
        from src.infrastructure.db.database import init_db
        
        if __name__ == "__main__":
            init_db()
            uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Elimina todas las tablas de la base de datos.
    
    Esta función elimina TODOS los datos.
    Usar solo en desarrollo o testing.
    
    Ejemplo:
        from src.infrastructure.db.database import drop_db
        drop_db()  # Elimina todo
        init_db()  # Recrea las tablas vacías
    """
    Base.metadata.drop_all(bind=engine)

from .import models