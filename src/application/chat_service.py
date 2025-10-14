from typing import List, Optional
from datetime import datetime
import asyncio
from ..domain.entities import Product, ChatMessage, ChatContext
from ..domain.repositories import IProductRepository, IChatRepository
from ..domain.exceptions import ChatServiceError, InvalidSessionError
from .dtos import ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO


class ChatService:
    """
    Servicio de aplicación para gestionar conversaciones de chat con IA.
    
    Orquesta la comunicación entre el usuario, el repositorio de chat,
    el repositorio de productos y el servicio de IA (Gemini).
    Mantiene contexto conversacional para respuestas coherentes.
    """
    
    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service
    ):
        """
        Inicializa el servicio de chat con inyección de dependencias.
        
        Args:
            product_repository: Repositorio para acceder a productos.
            chat_repository: Repositorio para guardar/recuperar mensajes.
            ai_service: Servicio de IA (Gemini) para generar respuestas.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service
    
    async def process_message(
        self,
        request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.
        
        Flujo:
        1. Obtiene todos los productos disponibles
        2. Recupera el historial reciente de la sesión
        3. Crea contexto conversacional
        4. Llama al servicio de IA para generar respuesta
        5. Guarda tanto el mensaje del usuario como la respuesta
        6. Retorna la respuesta formateada
        
        Args:
            request: DTO con session_id y mensaje del usuario.
            
        Retorna:
            ChatMessageResponseDTO: Respuesta del asistente con timestamp.
            
        Raises:
            ChatServiceError: Si hay error en el procesamiento.
            InvalidSessionError: Si la sesión es inválida.
        """
        try:
            # Validar que session_id no esté vacío
            if not request.session_id or request.session_id.strip() == "":
                raise InvalidSessionError(session_id=request.session_id)
            
            # 1. Obtener todos los productos del repositorio
            products = self.product_repository.get_all()
            
            # 2. Obtener historial reciente (últimos 6 mensajes)
            recent_messages = self.chat_repository.get_recent_messages(
                session_id=request.session_id,
                count=6
            )
            
            # 3. Crear contexto conversacional
            chat_context = ChatContext(
                messages=recent_messages,
                max_messages=6
            )
            
            # Preparar información de productos para el prompt
            products_info = self._format_products_for_prompt(products)
            context_text = chat_context.format_for_prompt()
            
            # 4. Llamar al servicio de IA para generar respuesta
            assistant_response = await self.ai_service.generate_response(
                user_message=request.message,
                products_info=products_info,
                conversation_context=context_text
            )
            
            # 5. Guardar mensaje del usuario
            user_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role='user',
                message=request.message,
                timestamp=datetime.utcnow()
            )
            saved_user_message = self.chat_repository.save_message(user_message_entity)
            
            # 6. Guardar respuesta del asistente
            assistant_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role='assistant',
                message=assistant_response,
                timestamp=datetime.utcnow()
            )
            saved_assistant_message = self.chat_repository.save_message(
                assistant_message_entity
            )
            
            # 7. Retornar respuesta formateada
            response = ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=saved_assistant_message.timestamp
            )
            
            return response
        
        except InvalidSessionError:
            raise
        except ChatServiceError:
            raise
        except Exception as e:
            raise ChatServiceError(
                message=f"Error procesando mensaje: {str(e)}"
            )
    
    async def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial completo de una sesión de chat.
        
        Args:
            session_id: Identificador único de la sesión.
            limit: Número máximo de mensajes a retornar (opcional).
                   Si no se especifica, retorna todos.
            
        Retorna:
            List[ChatHistoryDTO]: Lista de mensajes del historial en orden cronológico.
            
        Raises:
            InvalidSessionError: Si la sesión es inválida o no existe.
            ChatServiceError: Si hay error al recuperar el historial.
        """
        try:
            # Validar session_id
            if not session_id or session_id.strip() == "":
                raise InvalidSessionError(session_id=session_id)
            
            # Obtener mensajes del repositorio
            messages = self.chat_repository.get_session_history(
                session_id=session_id,
                limit=limit
            )
            
            # Convertir a DTOs
            history_dtos = [
                ChatHistoryDTO(
                    id=message.id,
                    role=message.role,
                    message=message.message,
                    timestamp=message.timestamp
                )
                for message in messages
            ]
            
            return history_dtos
        
        except InvalidSessionError:
            raise
        except Exception as e:
            raise ChatServiceError(
                message=f"Error obteniendo historial: {str(e)}"
            )
    
    async def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.
        
        Args:
            session_id: Identificador único de la sesión a limpiar.
            
        Retorna:
            int: Número de mensajes que fueron eliminados.
            
        Raises:
            InvalidSessionError: Si la sesión es inválida.
            ChatServiceError: Si hay error al eliminar el historial.
        """
        try:
            # Validar session_id
            if not session_id or session_id.strip() == "":
                raise InvalidSessionError(session_id=session_id)
            
            # Eliminar historial del repositorio
            deleted_count = self.chat_repository.delete_session_history(
                session_id=session_id
            )
            
            return deleted_count
        
        except InvalidSessionError:
            raise
        except Exception as e:
            raise ChatServiceError(
                message=f"Error limpiando historial: {str(e)}"
            )
    
    async def get_recent_context(
        self,
        session_id: str,
        count: int = 6
    ) -> ChatContext:
        """
        Obtiene el contexto conversacional reciente de una sesión.
        
        Útil para conocer el contexto actual sin procesar un mensaje.
        
        Args:
            session_id: Identificador de la sesión.
            count: Número de mensajes recientes a incluir (por defecto 6).
            
        Retorna:
            ChatContext: Contexto conversacional con los últimos mensajes.
            
        Raises:
            InvalidSessionError: Si la sesión es inválida.
            ChatServiceError: Si hay error al obtener el contexto.
        """
        try:
            if not session_id or session_id.strip() == "":
                raise InvalidSessionError(session_id=session_id)
            
            recent_messages = self.chat_repository.get_recent_messages(
                session_id=session_id,
                count=count
            )
            
            context = ChatContext(
                messages=recent_messages,
                max_messages=count
            )
            
            return context
        
        except InvalidSessionError:
            raise
        except Exception as e:
            raise ChatServiceError(
                message=f"Error obteniendo contexto: {str(e)}"
            )
    
    # Métodos privados auxiliares
    
    def _format_products_for_prompt(self, products: List[Product]) -> str:
        """
        Formatea la lista de productos para incluir en el prompt de IA.
        
        Crea una representación textual de los productos que la IA
        puede usar para generar respuestas contextualizadas.
        
        Args:
            products: Lista de productos del repositorio.
            
        Retorna:
            str: String con los productos formateados.
        """
        if not products:
            return "No hay productos disponibles."
        
        formatted_lines = [
            "Productos disponibles en el catálogo:"
        ]
        
        for product in products:
            # Incluir información relevante del producto
            availability = "Disponible" if product.is_available() else "Agotado"
            
            product_info = (
                f"- {product.name} ({product.brand}) | "
                f"Categoría: {product.category} | "
                f"Color: {product.color} | "
                f"Talla: {product.size} | "
                f"Precio: ${product.price:.2f} | "
                f"Stock: {product.stock} ({availability}) | "
                f"Descripción: {product.description}"
            )
            formatted_lines.append(product_info)
        
        return "\n".join(formatted_lines)
    
    def _validate_session_id(self, session_id: str) -> bool:
        """
        Valida que el session_id sea válido.
        
        Args:
            session_id: Session ID a validar.
            
        Retorna:
            bool: True si es válido, False en caso contrario.
        """
        return session_id and session_id.strip() != ""