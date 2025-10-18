# E-Commerce Chat AI

Sistema de e-commerce con asistente de chat inteligente impulsado por **Google Gemini AI**. Plataforma conversacional para consultar productos de calzado con recomendaciones personalizadas basadas en contexto e historial de conversación.

## Descripción del Proyecto

Aplicación que combina un catálogo de productos de calzado con un asistente virtual inteligente. Los usuarios pueden consultar sobre productos, obtener recomendaciones y recibir respuestas contextualizadas basadas en el historial conversacional de su sesión.

El sistema mantiene el contexto de las últimas 6 interacciones por sesión para generar respuestas coherentes y personalizadas. Utiliza Google Gemini AI (modelo `gemini-2.0-flash`) para procesar consultas y generar respuestas naturales sobre el catálogo de productos disponibles.

Implementa **Clean Architecture** con separación clara entre capas de dominio, aplicación e infraestructura, facilitando el mantenimiento y las pruebas unitarias.

## Características Principales

### Gestión de Productos
- **Catálogo de productos**: Zapatillas con información detallada (marca, categoría, talla, color, precio, stock)
- **Búsqueda y filtrado**: Por marca y categoría
- **Control de inventario**: Validaciones de stock con métodos de negocio (`reduce_stock`, `increase_stock`, `is_available`)
- **API RESTful**: Endpoints para consultas de productos

### Asistente de Chat Inteligente
- **Integración con Gemini AI**: Modelo `gemini-2.0-flash` para respuestas conversacionales
- **Contexto conversacional**: Mantiene historial de hasta 6 mensajes recientes por sesión
- **Recomendaciones personalizadas**: Sugiere productos del catálogo real basándose en preferencias del usuario
- **Gestión de sesiones**: Múltiples conversaciones independientes por `session_id`
- **Persistencia completa**: Todo el historial se guarda en base de datos

### Base de Datos
- **SQLite con SQLAlchemy ORM**: Almacenamiento local persistente
- **Dos tablas principales**:
  - `products`: Catálogo de productos con índices en `brand`, `category` y `name`
  - `chat_memory`: Historial de conversaciones con índice en `session_id`
- **Datos iniciales**: 10 productos precargados (Nike, Adidas, Puma, New Balance, Converse)

## Arquitectura

### Clean Architecture - Separación por Capas

```
┌─────────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                        │
│           src/infrastructure/api/main.py                │
│     Endpoints REST, middleware CORS, validación        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Application Layer                             │
│              src/application/                           │
│   ProductService, ChatService, DTOs (Pydantic)          │
│   (Orquestación de casos de uso)                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Domain Layer                               │
│              src/domain/                                │
│   Entities: Product, ChatMessage, ChatContext           │
│   Repositories: IProductRepository, IChatRepository     │
│   Exceptions: ProductNotFoundError, ChatServiceError    │
│   (Lógica de negocio pura, sin dependencias)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Infrastructure Layer                            │
│         src/infrastructure/                             │
│  - Repositories: SQLProductRepository, SQLChatRepository│
│  - Models ORM: ProductModel, ChatMemoryModel            │
│  - LLM: GeminiService (google-generativeai)             │
│  - Database: SQLite + SQLAlchemy                        │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Procesamiento de Mensaje de Chat

```
1. Cliente envía POST /chat
       │
       ▼
2. ChatService.process_message()
       │
       ├─→ ProductRepository.get_all()
       │   (Obtiene catálogo completo)
       │
       ├─→ ChatRepository.get_recent_messages(count=6)
       │   (Recupera últimos 6 mensajes de la sesión)
       │
       ├─→ ChatContext.format_for_prompt()
       │   (Construye contexto conversacional)
       │
       ├─→ GeminiService.generate_response()
       │   (Llama a Gemini AI con prompt completo)
       │
       ├─→ ChatRepository.save_message(user_message)
       │   (Guarda mensaje del usuario)
       │
       ├─→ ChatRepository.save_message(assistant_message)
       │   (Guarda respuesta del asistente)
       │
       ▼
3. Retorna ChatMessageResponseDTO al cliente
```

### Componentes Principales

#### Capa de Dominio (`src/domain/`)
- **`Product`**: Entidad con validaciones (`price > 0`, `stock >= 0`, `name` no vacío) y métodos de negocio
- **`ChatMessage`**: Entidad con validación de `role` ('user' o 'assistant'), `session_id` y `message`
- **`ChatContext`**: Value Object que encapsula contexto conversacional (últimos N mensajes)
- **`IProductRepository`**: Interface para acceso a productos
- **`IChatRepository`**: Interface para historial de chat
- **Excepciones**: `ProductNotFoundError`, `InvalidProductDataError`, `ChatServiceError`, `InvalidSessionError`, `InsufficientStockError`

#### Capa de Aplicación (`src/application/`)
- **`ProductService`**: CRUD de productos, búsquedas, gestión de stock
- **`ChatService`**: Procesamiento de mensajes, gestión de contexto, integración con IA
- **DTOs**: `ProductDTO`, `ChatMessageRequestDTO`, `ChatMessageResponseDTO`, `ChatHistoryDTO`

#### Capa de Infraestructura (`src/infrastructure/`)
- **`SQLProductRepository`**: Implementación con SQLAlchemy
- **`SQLChatRepository`**: Persistencia de mensajes con consultas por sesión
- **`GeminiService`**: Integración con Google Gemini AI
- **`ProductModel`**, **`ChatMemoryModel`**: Modelos ORM con índices optimizados
- **`main.py`**: Aplicación FastAPI con endpoints y lifecycle management

## Instalación

### Requisitos Previos
- **Python 3.11 o superior**
- **Docker y Docker Compose** (opcional)
- **Cuenta de Google Cloud** con acceso a Gemini API

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd e-commerce-chat-ai
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_clave_api_de_gemini
DATABASE_URL=sqlite:///./data/ecommerce.db
```

5. **Iniciar la aplicación**

La base de datos se crea automáticamente al iniciar. Los datos iniciales (10 productos) se cargan en el primer arranque.

```bash
uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en `http://localhost:8000`

### Instalación con Docker

1. **Configurar variables de entorno**

Crear archivo `.env`:
```env
GEMINI_API_KEY=tu_clave_api
DATABASE_URL=sqlite:///./data/ecommerce.db
```

2. **Construir y ejecutar**
```bash
docker-compose up --build
```

3. **Acceder a la aplicación**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `GEMINI_API_KEY` | API Key de Google Gemini (obligatoria) | - |
| `DATABASE_URL` | URL de conexión a base de datos SQLite | `sqlite:///./data/ecommerce.db` |

### Configuración de Gemini AI

El servicio utiliza los siguientes parámetros para el modelo `gemini-2.0-flash`:

```python
{
    "temperature": 0.7,        # Balance creatividad/determinismo
    "top_p": 0.95,            # Diversidad en tokens
    "top_k": 40,              # Top-40 tokens considerados
    "max_output_tokens": 500  # Límite de respuesta
}
```

## Uso

### Endpoints de la API

#### Información

**Obtener información de la API**
```http
GET /
```

**Respuesta:**
```json
{
  "nombre": "E-Commerce Chat API",
  "versión": "1.0.0",
  "descripción": "API para e-commerce con asistente de chat inteligente",
  "endpoints": { ... }
}
```

**Health check**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T10:30:00.000Z",
  "service": "E-Commerce Chat API"
}
```

#### Productos

**Listar todos los productos**
```http
GET /products
```

**Obtener producto por ID**
```http
GET /products/{product_id}
```

**Buscar por categoría**
```http
GET /products/category/{category}
```
Categorías disponibles: `Running`, `Casual`, `Formal`, `Training`

**Buscar por marca**
```http
GET /products/brand/{brand}
```
Marcas disponibles: `Nike`, `Adidas`, `Puma`, `New Balance`, `Converse`

#### Chat

**Enviar mensaje al asistente**
```http
POST /chat
Content-Type: application/json

{
  "session_id": "user_session_123",
  "message": "¿Qué zapatillas de running tienen?"
}
```

**Respuesta:**
```json
{
  "session_id": "user_session_123",
  "user_message": "¿Qué zapatillas de running tienen?",
  "assistant_message": "Tenemos varias opciones de zapatillas para running. Te recomiendo las Nike Air Max 90 ($129.99, talla 42) con tecnología Air Max para máxima amortiguación, o las Adidas Ultra Boost 21 ($159.99, talla 41) con tecnología Boost. ¿Tienes preferencia de marca o presupuesto?",
  "timestamp": "2025-10-14T10:30:00.000Z"
}
```

**Obtener historial de sesión**
```http
GET /chat/history/{session_id}?limit=10
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "role": "user",
    "message": "¿Qué zapatillas de running tienen?",
    "timestamp": "2025-10-14T10:30:00.000Z"
  },
  {
    "id": 2,
    "role": "assistant",
    "message": "Tenemos varias opciones...",
    "timestamp": "2025-10-14T10:30:05.000Z"
  }
]
```

**Eliminar historial de sesión**
```http
DELETE /chat/history/{session_id}
```

**Respuesta:**
```json
{
  "message": "Se eliminaron 10 mensajes",
  "deleted_count": 10,
  "session_id": "user_session_123"
}
```

### Ejemplo de Conversación Contextual

**Primer mensaje:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_abc",
    "message": "Busco zapatillas para correr"
  }'
```

**Segunda consulta (con contexto):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_abc",
    "message": "Prefiero Nike, ¿cuál me recomiendas?"
  }'
```

El asistente recordará que estás buscando zapatillas para correr y ajustará su recomendación de Nike específicamente para running.

## Testing

### Estructura de Tests

El proyecto incluye tests unitarios en `tests/`:
- `test_entities.py`: Tests de entidades de dominio (Product, ChatMessage, ChatContext)
- `test_services.py`: Tests de servicios de aplicación (ProductService, ChatService)
- `conftest.py`: Fixtures compartidos (base de datos de prueba, cliente HTTP)

### Ejecutar Tests

**Todos los tests:**
```bash
pytest
```

**Con información detallada:**
```bash
pytest -v
```

**Con cobertura de código:**
```bash
pytest --cov=src --cov-report=term-missing
```

**Generar reporte HTML de cobertura:**
```bash
pytest --cov=src --cov-report=html
```

El reporte se genera en `htmlcov/index.html`

**Tests específicos:**
```bash
# Solo tests de entidades
pytest tests/test_entities.py

# Solo tests de servicios
pytest tests/test_services.py

# Test específico por nombre
pytest tests/test_entities.py::TestProduct::test_product_creation_valid
```

### Configuración de Pytest

El archivo `tests/pyproject.toml` contiene la configuración:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

### Cobertura de Tests

El proyecto incluye tests para:
- ✅ Validaciones de entidades de dominio
- ✅ Lógica de negocio (stock, disponibilidad, roles)
- ✅ Servicios de aplicación (CRUD, búsquedas)
- ✅ Gestión de contexto conversacional
- ✅ Manejo de errores y excepciones
- ✅ Casos extremos y validaciones de límites

## Docker

### Construcción de la Imagen

El `Dockerfile` utiliza Python 3.11-slim:

```bash
# Construir imagen
docker build -t ecommerce-chat-ai .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=tu_api_key \
  -e DATABASE_URL=sqlite:///./data/ecommerce.db \
  -v $(pwd)/data:/app/data \
  ecommerce-chat-ai
```

### Docker Compose

El archivo `docker-compose.yml` configura:
- Puerto `8000:8000`
- Variables de entorno desde `.env`
- Volume para persistencia de datos (`./data:/app/data`)
- Healthcheck cada 30 segundos
- Modo desarrollo con `--reload`
- Red bridge `app-network`

**Comandos:**

```bash
# Iniciar servicios
docker-compose up

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir y reiniciar
docker-compose up --build
```

### Healthcheck

El contenedor incluye healthcheck que verifica el endpoint `/health`:
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Reintentos: 3
- Período de inicio: 15 segundos

## Tecnologías Utilizadas

### Backend
- **Python 3.11**: Lenguaje de programación principal
- **FastAPI 0.104.1**: Framework web asíncrono de alto rendimiento
- **Uvicorn 0.24.0**: Servidor ASGI para FastAPI
- **Pydantic 2.5.0**: Validación de datos y serialización

### Base de Datos
- **SQLAlchemy 2.0.23**: ORM para Python
- **SQLite**: Base de datos embebida (persistencia local)

### Inteligencia Artificial
- **google-generativeai 0.3.1**: Cliente oficial de Google Gemini
- **Modelo**: `gemini-2.0-flash` (generación conversacional)

### Utilidades
- **python-dotenv 1.0.0**: Carga de variables de entorno
- **httpx 0.25.1**: Cliente HTTP asíncrono

### Testing
- **pytest 8.4.2**: Framework de testing
- **pytest-asyncio 1.2.0**: Soporte para tests asíncronos
- **pytest-cov**: Medición de cobertura de código
- **unittest.mock**: Mocking de dependencias

### DevOps
- **Docker**: Containerización de la aplicación
- **Docker Compose**: Orquestación de servicios

## Estructura del Proyecto

```
e-commerce-chat-ai/
│
├── src/
│   ├── __init__.py
│   │
│   ├── domain/                    # Capa de dominio
│   │   ├── __init__.py
│   │   ├── entities.py           # Product, ChatMessage, ChatContext
│   │   ├── repositories.py       # IProductRepository, IChatRepository
│   │   └── exceptions.py         # Excepciones de negocio
│   │
│   ├── application/              # Capa de aplicación
│   │   ├── __init__.py
│   │   ├── product_service.py   # Lógica de productos
│   │   ├── chat_service.py      # Lógica de chat
│   │   └── dtos.py              # Data Transfer Objects (Pydantic)
│   │
│   └── infrastructure/           # Capa de infraestructura
│       ├── __init__.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   └── main.py          # App FastAPI, endpoints, middleware
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── database.py      # Config SQLAlchemy, SessionLocal
│       │   ├── models.py        # ProductModel, ChatMemoryModel
│       │   └── init_data.py     # Carga de 10 productos iniciales
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── product_repository.py   # SQLProductRepository
│       │   └── chat_repository.py      # SQLChatRepository
│       │
│       └── llm_providers/
│           ├── __init__.py
│           └── gemini_service.py       # GeminiService
│
├── tests/                        # Tests unitarios
│   ├── __init__.py
│   ├── conftest.py              # Fixtures (test_db, client)
│   ├── test_entities.py         # Tests de Product, ChatMessage, ChatContext
│   ├── test_services.py         # Tests de ProductService, ChatService
│   └── pyproject.toml           # Configuración de pytest
│
├── data/                         # Base de datos SQLite (creada en runtime)
│   └── ecommerce.db             # (generado automáticamente)
│
├── docker-compose.yml            # Orquestación Docker
├── Dockerfile                    # Imagen Docker (Python 3.11-slim)
├── requirements.txt              # Dependencias Python
├── .env                          # Variables de entorno (no versionado)
├── .gitignore
└── README.md
```

### Descripción de Módulos

#### `src/domain/`
Capa de lógica de negocio pura, sin dependencias de infraestructura:
- **`entities.py`**: Clases `Product`, `ChatMessage`, `ChatContext` con validaciones y métodos de negocio
- **`repositories.py`**: Interfaces abstractas que definen contratos para repositorios
- **`exceptions.py`**: Excepciones específicas del dominio

#### `src/application/`
Casos de uso y orquestación de lógica de negocio:
- **`product_service.py`**: CRUD, búsquedas, gestión de stock
- **`chat_service.py`**: Procesamiento de mensajes, gestión de contexto, integración con IA
- **`dtos.py`**: Objetos de transferencia de datos con validaciones Pydantic

#### `src/infrastructure/`
Implementaciones concretas y dependencias externas:
- **`api/main.py`**: 11 endpoints REST, middleware CORS, manejo de errores
- **`db/`**: SQLAlchemy, modelos ORM, funciones de inicialización
- **`repositories/`**: Implementaciones SQL de interfaces de repositorios
- **`llm_providers/`**: Integración con Google Gemini AI

#### `tests/`
Tests unitarios con fixtures compartidos y mocks de dependencias

## Manejo de Errores

### Excepciones de Dominio

| Excepción | Descripción | Código HTTP |
|-----------|-------------|-------------|
| `ProductNotFoundError` | Producto no existe | 404 |
| `InvalidProductDataError` | Datos de producto inválidos | 400 |
| `ChatServiceError` | Error en servicio de chat | 500 |
| `InvalidSessionError` | Session ID inválido | 400 |
| `InsufficientStockError` | Stock insuficiente | 400 |

### Formato de Respuestas de Error

```json
{
  "error": true,
  "status_code": 404,
  "detail": "Producto con ID 999 no encontrado",
  "timestamp": "2025-10-14T10:30:00.000Z"
}
```

## Datos Iniciales

El sistema carga automáticamente 10 productos en el primer arranque:

| ID | Producto | Marca | Categoría | Precio | Stock |
|----|----------|-------|-----------|--------|-------|
| 1 | Nike Air Max 90 | Nike | Running | $129.99 | 15 |
| 2 | Adidas Ultra Boost 21 | Adidas | Running | $159.99 | 8 |
| 3 | Puma RS-X | Puma | Casual | $89.99 | 22 |
| 4 | New Balance 574 | New Balance | Casual | $99.99 | 18 |
| 5 | Converse Chuck Taylor | Converse | Casual | $59.99 | 35 |
| 6 | Nike Court Legacy | Nike | Formal | $74.99 | 12 |
| 7 | Adidas NMD R1 | Adidas | Training | $139.99 | 10 |
| 8 | Puma Future Rider | Puma | Running | $85.99 | 0 |
| 9 | Nike ZoomX Vaporfly | Nike | Running | $199.99 | 5 |
| 10 | Adidas Superstar | Adidas | Casual | $79.99 | 28 |

## Contribución

[Información no disponible en el código]

## Licencia

[Información no disponible en el código]

---

**Documentación Adicional:**
- [Swagger UI Interactive](http://localhost:8000/docs)
- [ReDoc Documentation](http://localhost:8000/redoc)
