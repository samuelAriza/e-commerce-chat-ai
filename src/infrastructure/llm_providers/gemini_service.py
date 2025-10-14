import os
import asyncio
from typing import List, Optional
import google.generativeai as genai
from ...domain.entities import Product


class GeminiService:
    """
    Servicio de integración con Google Gemini AI.
    
    Proporciona generación de respuestas conversacionales usando el modelo
    gemini-2.5-flash. Mantiene contexto de productos y conversación anterior
    para dar respuestas personalizadas y coherentes.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de Gemini.
        
        - Carga la clave API desde variables de entorno
        - Configura el cliente de Gemini
        - Inicializa el modelo gemini-2.5-flash
        
        Raises:
            ValueError: Si GEMINI_API_KEY no está definida en variables de entorno.
        """
        # Obtener API key de variables de entorno
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no está definida. "
                "Por favor, define la variable de entorno GEMINI_API_KEY"
            )
        
        # Configurar cliente de Gemini
        genai.configure(api_key=self.api_key)
        
        # Inicializar modelo
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        print("Servicio Gemini inicializado correctamente")
    
    async def generate_response(
        self,
        user_message: str,
        products_info: str,
        conversation_context: str
    ) -> str:
        """
        Genera una respuesta de IA basada en el mensaje del usuario y contexto.
        
        Flujo:
        1. Construye el prompt del sistema con instrucciones
        2. Incluye lista de productos disponibles
        3. Añade historial de conversación para coherencia
        4. Añade el mensaje actual del usuario
        5. Llama a Gemini API
        6. Retorna la respuesta generada
        
        Args:
            user_message: Mensaje actual del usuario.
            products_info: String con lista de productos formateada.
            conversation_context: Historial de conversación anterior formateado.
            
        Retorna:
            str: Respuesta generada por Gemini.
            
        Raises:
            Exception: Si hay error en la llamada a la API.
        """
        try:
            # Construir el prompt
            prompt = self._build_prompt(
                user_message=user_message,
                products_info=products_info,
                conversation_context=conversation_context
            )
            
            # Llamar a Gemini en thread separado para no bloquear
            # Simular operacion async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._call_gemini_api,
                prompt
            )
            
            return response
        
        except Exception as e:
            print(f"Error generando respuesta con Gemini: {str(e)}")
            raise
    
    def _build_prompt(
        self,
        user_message: str,
        products_info: str,
        conversation_context: str
    ) -> str:
        """
        Construye el prompt completo para Gemini.
        
        Combina instrucciones del sistema, lista de productos,
        historial conversacional y mensaje actual en un prompt coherente.
        
        Args:
            user_message: Mensaje actual del usuario.
            products_info: Información de productos disponibles.
            conversation_context: Historial de conversación.
            
        Retorna:
            str: Prompt completo para enviar a Gemini.
        """
        system_prompt = """Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
        Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

        INSTRUCCIONES:
        - Sé amigable, profesional y entusiasta
        - Usa el contexto de la conversación anterior para mantener coherencia
        - Recomienda productos específicos cuando sea apropiado
        - Menciona siempre precios, tallas y disponibilidad cuando recomiendes
        - Si un cliente pregunta sobre productos específicos, usa la lista disponible
        - Si no tienes información sobre algo, sé honesto y ofrece ayuda alternativa
        - Mantén las respuestas concisas pero informativas (máximo 3-4 oraciones)
        - Si un producto está agotado, sugiere alternativas similares disponibles
        - Siempre sé respetuoso y considerado con las preferencias del cliente

        PRODUCTOS DISPONIBLES EN EL CATÁLOGO:
        {products_info}

        HISTORIAL DE CONVERSACIÓN PREVIA:
        {conversation_context}

        Usuario: {user_message}

        Asistente:"""
        
        # Formatear el prompt con la información real
        formatted_prompt = system_prompt.format(
            products_info=products_info,
            conversation_context=conversation_context,
            user_message=user_message
        )
        
        return formatted_prompt
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Realiza la llamada a la API de Gemini de forma síncrona.
        
        Este método se ejecuta en un thread separado por `run_in_executor`
        para simular una operación async.
        
        Args:
            prompt: Prompt completo para enviar a Gemini.
            
        Retorna:
            str: Texto de la respuesta generada.
            
        Raises:
            Exception: Si hay error en la API.
        """
        try:
            # Configurar parámetros de generación
            generation_config = {
                "temperature": 0.7,  # Equilibrio entre determinístico y creativo
                "top_p": 0.95,       # Diversidad en tokens
                "top_k": 40,         # Consideración de top-40 tokens
                "max_output_tokens": 500,  # Limitar longitud de respuesta
            }
            
            # Realizar llamada a Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extraer texto de la respuesta
            if response.text:
                return response.text.strip()
            else:
                return "Lo siento, no pude generar una respuesta. Por favor, intenta de nuevo."
        
        except Exception as e:
            print(f"Error en llamada a Gemini API: {str(e)}")
            raise
    
    def format_products_info(self, products: List[Product]) -> str:
        """
        Formatea una lista de entidades Product a texto legible para Gemini.
        
        Cada producto se representa en una línea con información clave:
        "- Nombre | Marca | Precio | Stock"
        
        Args:
            products: Lista de entidades Product del dominio.
            
        Retorna:
            str: String con productos formateados, uno por línea.
        """
        if not products:
            return "No hay productos disponibles en este momento."
        
        formatted_lines = []
        
        for product in products:
            # Determinar disponibilidad
            availability = "Disponible" if product.is_available() else "AGOTADO"
            
            # Formatear línea del producto
            product_line = (
                f"- {product.name} | "
                f"Marca: {product.brand} | "
                f"Categoría: {product.category} | "
                f"Color: {product.color} | "
                f"Talla: {product.size} | "
                f"Precio: ${product.price:.2f} | "
                f"Stock: {product.stock} ({availability})"
            )
            formatted_lines.append(product_line)
        
        return "\n".join(formatted_lines)