from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from ...domain.entities import ChatMessage
from ...domain.repositories import IChatRepository
from ..db.models import ChatMemoryModel

class SQLChatRepository(IChatRepository):
    """
    Implementación del repositorio de chat usando SQLAlchemy y SQLite.
    
    Implementa la interface IChatRepository con operaciones CRUD
    sobre la tabla de historial de chat en la base de datos.
    Mantiene el orden cronológico de los mensajes para contexto conversacional.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de BD.
        
        Args:
            db: Sesión de SQLAlchemy inyectada desde FastAPI.
        """
        self.db = db
    
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje de chat en la base de datos.
        
        Si el mensaje no tiene ID, se crea uno nuevo.
        Si el mensaje tiene ID, se actualiza el existente.
        
        Args:
            message: Entidad ChatMessage a guardar.
            
        Retorna:
            ChatMessage: El mensaje guardado con su ID asignado.
            
        Raises:
            Exception: Si hay error al guardar en la BD.
        """
        try:
            # Convierte la entidad del dominio a modelo ORM
            message_model = self._entity_to_model(message)
            
            if message.id is not None:
                # Actualizar mensaje existente
                message_model = self.db.merge(message_model)
            else:
                # Crear nuevo mensaje
                self.db.add(message_model)
            
            # Hacer commit para guardar cambios
            self.db.commit()
            
            # Refresh para obtener el ID si fue creado
            self.db.refresh(message_model)
            
            # Convierte el modelo guardado a entidad del dominio
            saved_message = self._model_to_entity(message_model)
            
            return saved_message
        
        except Exception as e:
            print(f"Error guardando mensaje: {str(e)}")
            self.db.rollback()
            raise
    
    def get_session_history(
    self,
    session_id: str,
    limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo de una sesión conversacional.
        
        Los mensajes se retornan en orden cronológico (más antiguos primero).
        """
        try:
            # Base query filtrada por session_id
            query = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.asc())  # ✅ primero ordenamos
            )
            
            # Aplicar limit si se especifica (después del order_by)
            if limit is not None:
                query = query.limit(limit)  # ✅ ahora sí aplicamos el límite
            
            # Ejecutar consulta
            message_models = query.all()
            
            # Convertir modelos a entidades
            messages = [self._model_to_entity(model) for model in message_models]
            
            return messages

        except Exception as e:
            print(f"Error obteniendo historial de la sesión '{session_id}': {str(e)}")
            return []

    
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.
        
        Args:
            session_id: El identificador único de la sesión a eliminar.
            
        Retorna:
            int: Cantidad de mensajes que fueron eliminados.
                 Retorna 0 si la sesión no existía o estaba vacía.
        """
        try:
            # Contar cuántos mensajes se van a eliminar
            messages_count = self.db.query(ChatMemoryModel).filter(
                ChatMemoryModel.session_id == session_id
            ).count()
            
            # Si no hay mensajes, retornar 0
            if messages_count == 0:
                return 0
            
            # Eliminar todos los mensajes de la sesión
            self.db.query(ChatMemoryModel).filter(
                ChatMemoryModel.session_id == session_id
            ).delete()
            
            # Hacer commit
            self.db.commit()
            
            return messages_count
        
        except Exception as e:
            print(f"Error eliminando historial de la sesión '{session_id}': {str(e)}")
            self.db.rollback()
            return 0
    
    def get_recent_messages(
        self,
        session_id: str,
        count: int
    ) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión.
        
        Este método es crucial para mantener el contexto conversacional
        reciente cuando se envía información a la IA.
        Los mensajes se retornan en orden cronológico (más antiguos primero).
        
        Ejemplo: Si count=6 y hay 10 mensajes, retorna los últimos 6
        pero en orden antiguo→nuevo para mantener coherencia conversacional.
        
        Args:
            session_id: El identificador único de la sesión.
            count: Número de últimos mensajes a retornar.
            
        Retorna:
            List[ChatMessage]: Lista con los últimos N mensajes en orden cronológico.
                              Retorna menos mensajes si la sesión tiene menos de N.
                              Retorna lista vacía si la sesión no existe.
        """
        try:
            # Query para obtener los últimos N mensajes de la sesión
            # Ordenamos DESC para obtener los más recientes
            recent_message_models = self.db.query(ChatMemoryModel).filter(
                ChatMemoryModel.session_id == session_id
            ).order_by(
                desc(ChatMemoryModel.timestamp)
            ).limit(count).all()
            
            # Invertimos la lista para que quede en orden cronológico ascendente
            # (antiguos primero, recientes últimos)
            recent_message_models.reverse()
            
            # Convierte modelos a entidades
            messages = [self._model_to_entity(model) for model in recent_message_models]
            
            return messages
        
        except Exception as e:
            print(f"Error obteniendo últimos {count} mensajes de '{session_id}': {str(e)}")
            return []
    
    # Métodos privados
    
    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM (ChatMemoryModel) a una entidad del dominio (ChatMessage).
        
        Args:
            model: Modelo ORM de la base de datos.
            
        Retorna:
            ChatMessage: Entidad del dominio con los mismos datos.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp
        )
    
    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad del dominio (ChatMessage) a modelo ORM (ChatMemoryModel).
        
        Args:
            entity: Entidad del dominio.
            
        Retorna:
            ChatMemoryModel: Modelo ORM listo para guardar en BD.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp
        )