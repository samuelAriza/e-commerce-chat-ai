from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
import asyncio
from ..db.database import init_db, get_db
from ..db.init_data import load_initial_data
from ..db.models import ProductModel, ChatMemoryModel
from ..repositories.product_repository import SQLProductRepository
from ..repositories.chat_repository import SQLChatRepository
from ..llm_providers.gemini_service import GeminiService
from ...application.product_service import ProductService
from ...application.chat_service import ChatService
from ...application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO
)
from ...domain.exceptions import (
    ProductNotFoundError,
    ChatServiceError,
    InvalidSessionError
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Reemplazo de los eventos startup y shutdown usando el ciclo de vida moderno.
    """
    global gemini_service

    print("Iniciando aplicación E-Commerce Chat API...")
    try:
        # Inicializar base de datos
        print("Inicializando base de datos...")
        init_db()
        load_initial_data()
        print("Base de datos lista")

        # Inicializar Gemini
        print("Inicializando servicio de IA (Gemini)...")
        gemini_service = GeminiService()
        print("Servicio de IA listo")

        print("Aplicación iniciada correctamente\n")
        yield  # ← Aquí FastAPI deja correr la app

    except Exception as e:
        print(f"Error durante startup: {str(e)}")
        raise

    finally:
        # Equivalente al shutdown
        print("Aplicación detenida")

app = FastAPI(
    title="E-Commerce Chat API",
    description="API para e-commerce con asistente de chat inteligente impulsado por Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configurar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable global para servicio de Gemini
gemini_service: Optional[GeminiService] = None

@app.get("/", tags=["Información"])
async def root():
    """
    Retorna información básica de la API.
    
    Returns:
        dict: Información sobre la API, versión y endpoints disponibles.
    """
    return {
        "nombre": "E-Commerce Chat API",
        "versión": "1.0.0",
        "descripción": "API para e-commerce con asistente de chat inteligente",
        "endpoints": {
            "productos": [
                "GET /products - Listar todos los productos",
                "GET /products/{product_id} - Obtener producto por ID"
            ],
            "chat": [
                "POST /chat - Enviar mensaje al chat",
                "GET /chat/history/{session_id} - Obtener historial de sesión",
                "DELETE /chat/history/{session_id} - Eliminar historial de sesión"
            ],
            "utilidad": [
                "GET /health - Health check",
                "GET /docs - Documentación interactiva (Swagger)",
                "GET /redoc - Documentación ReDoc"
            ]
        }
    }

@app.get("/products", response_model=List[ProductDTO], tags=["Productos"])
async def get_all_products(db: Session = Depends(get_db)):
    """
    Obtiene todos los productos disponibles.
    
    Returns:
        List[ProductDTO]: Lista de todos los productos en el catálogo.
        
    Raises:
        HTTPException 500: Si hay error al obtener productos.
    """
    try:
        # Crear repositorio y servicio
        repository = SQLProductRepository(db=db)
        service = ProductService(repository=repository)
        
        # Obtener productos
        products = service.get_all_products()
        
        return products
    
    except Exception as e:
        print(f"Error obteniendo productos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener productos")


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["Productos"])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto específico por su ID.
    
    Args:
        product_id: Identificador del producto.
        
    Returns:
        ProductDTO: Datos del producto solicitado.
        
    Raises:
        HTTPException 404: Si el producto no existe.
        HTTPException 500: Si hay error al obtener el producto.
    """
    try:
        # Crear repositorio y servicio
        repository = SQLProductRepository(db=db)
        service = ProductService(repository=repository)
        
        # Obtener producto
        product = service.get_product_by_id(product_id)
        
        return product
    
    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    except Exception as e:
        print(f"Error obteniendo producto {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener producto")


@app.get("/products/category/{category}", response_model=List[ProductDTO], tags=["Productos"])
async def get_products_by_category(category: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los productos de una categoría específica.
    
    Args:
        category: Nombre de la categoría (ej: Running, Casual, Formal).
        
    Returns:
        List[ProductDTO]: Lista de productos de la categoría.
        
    Raises:
        HTTPException 500: Si hay error en la búsqueda.
    """
    try:
        repository = SQLProductRepository(db=db)
        service = ProductService(repository=repository)
        
        products = service.search_products({"category": category})
        
        return products
    
    except Exception as e:
        print(f"Error obteniendo productos de categoría '{category}': {str(e)}")
        raise HTTPException(status_code=500, detail="Error al buscar productos")


@app.get("/products/brand/{brand}", response_model=List[ProductDTO], tags=["Productos"])
async def get_products_by_brand(brand: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los productos de una marca específica.
    
    Args:
        brand: Nombre de la marca (ej: Nike, Adidas, Puma).
        
    Returns:
        List[ProductDTO]: Lista de productos de la marca.
        
    Raises:
        HTTPException 500: Si hay error en la búsqueda.
    """
    try:
        repository = SQLProductRepository(db=db)
        service = ProductService(repository=repository)
        
        products = service.search_products({"brand": brand})
        
        return products
    
    except Exception as e:
        print(f"Error obteniendo productos de la marca '{brand}': {str(e)}")
        raise HTTPException(status_code=500, detail="Error al buscar productos")

@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["Chat"])
async def send_chat_message(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db)
):
    """
    Procesa un mensaje del usuario y genera respuesta con IA.
    
    Args:
        request: DTO con session_id y mensaje del usuario.
        db: Sesión de base de datos.
        
    Returns:
        ChatMessageResponseDTO: Respuesta del asistente con timestamp.
        
    Raises:
        HTTPException 400: Si el mensaje o sesión son inválidos.
        HTTPException 500: Si hay error al procesar el mensaje.
    """
    try:
        # Validar que gemini_service está inicializado
        if not gemini_service:
            raise HTTPException(
                status_code=503,
                detail="Servicio de IA no disponible"
            )
        
        # Crear repositorios y servicio
        product_repository = SQLProductRepository(db=db)
        chat_repository = SQLChatRepository(db=db)
        
        service = ChatService(
            product_repository=product_repository,
            chat_repository=chat_repository,
            ai_service=gemini_service
        )
        
        # Procesar mensaje
        response = await service.process_message(request)
        
        return response
    
    except InvalidSessionError as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        print(f"Error procesando mensaje de chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar el mensaje"
        )

@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO], tags=["Chat"])
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de una sesión de chat.
    
    Args:
        session_id: Identificador de la sesión.
        limit: Máximo de mensajes a retornar (default: 10, máx: 100).
        db: Sesión de base de datos.
        
    Returns:
        List[ChatHistoryDTO]: Historial de mensajes de la sesión.
        
    Raises:
        HTTPException 400: Si la sesión es inválida.
        HTTPException 500: Si hay error al obtener el historial.
    """
    try:
        # Crear repositorio y servicio
        chat_repository = SQLChatRepository(db=db)
        product_repository = SQLProductRepository(db=db)
        
        service = ChatService(
            product_repository=product_repository,
            chat_repository=chat_repository,
            ai_service=gemini_service
        )
        
        # Obtener historial
        history = await service.get_session_history(
            session_id=session_id,
            limit=limit
        )
        
        return history
    
    except InvalidSessionError as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        print(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener historial"
        )

@app.delete("/chat/history/{session_id}", tags=["Chat"])
async def delete_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina todo el historial de una sesión de chat.
    
    Args:
        session_id: Identificador de la sesión a limpiar.
        db: Sesión de base de datos.
        
    Returns:
        dict: Cantidad de mensajes eliminados.
        
    Raises:
        HTTPException 400: Si la sesión es inválida.
        HTTPException 500: Si hay error al eliminar el historial.
    """
    try:
        # Crear repositorio y servicio
        chat_repository = SQLChatRepository(db=db)
        product_repository = SQLProductRepository(db=db)
        
        service = ChatService(
            product_repository=product_repository,
            chat_repository=chat_repository,
            ai_service=gemini_service
        )
        
        # Eliminar historial
        deleted_count = await service.clear_session_history(session_id)
        
        return {
            "message": f"Se eliminaron {deleted_count} mensajes",
            "deleted_count": deleted_count,
            "session_id": session_id
        }
    
    except InvalidSessionError as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        print(f"Error eliminando historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar historial"
        )

@app.get("/health", tags=["Utilidad"])
async def health_check():
    """
    Health check endpoint.
    
    Verifica que la API está funcionando correctamente.
    
    Returns:
        dict: Estado de la API y timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "E-Commerce Chat API"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja excepciones HTTP."""
    return {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }