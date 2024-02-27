from abc import ABC, abstractmethod
from typing import Dict, Any
from models import Message  # Asegúrate de que esta importación sea correcta según tu estructura de proyecto

class ProcessingStrategy(ABC):
    """
    Clase abstracta que define la interfaz para las estrategias de procesamiento.
    Las subclases deben implementar el método process.
    """
    
    @abstractmethod
    async def process(self, data: Any):  # Cambiado Dict[str, Any] por Any para permitir mayor flexibilidad en los datos de entrada.
        """
        Método abstracto para procesar los datos de entrada.
        
        Args:
            data (Any): Los datos a procesar. El tipo Any permite una mayor flexibilidad.
        """
        pass

class MessageProcessingStrategy(ProcessingStrategy):
    """
    Estrategia para procesar mensajes. Implementa el método process para trabajar con modelos Pydantic de mensajes.
    """
    
    async def process(self, message: Message):  # Tipo de entrada específica para reflejar el modelo Pydantic.
        """
        Procesa un mensaje.
        
        Args:
            message (Message): El mensaje a procesar.
        """
        print(f"Mensaje recibido: {message.text.body if message.text else 'No body'}")

class MediaProcessingStrategy(ProcessingStrategy):
    """
    Estrategia para procesar medios. Implementa el método process para manejar diferentes tipos de medios.
    """
    
    async def process(self, message: Message):
        """
        Procesa un mensaje que contiene medios (imagen, voz, video).
        
        Args:
            message (Message): El mensaje que contiene el medio a procesar.
        """
        # El procesamiento varía según el tipo de medio en el mensaje.
        # Se muestra un ejemplo de cómo manejar cada tipo.
        if message.type == 'image' and message.image:
            media_id = message.image.id
            print(f"Descargando imagen con media_id: {media_id}")
            # Aquí podría ir lógica adicional para manejar la descarga y el almacenamiento del medio.
        elif message.type == 'voice' and message.voice:
            media_id = message.voice.id
            print(f"Descargando voz con media_id: {media_id}")
        elif message.type == 'video' and message.video:
            media_id = message.video.id
            print(f"Descargando video con media_id: {media_id}")
        else:
            print("Tipo de mensaje no manejado por esta estrategia.")

class StatusUpdateProcessingStrategy(ProcessingStrategy):
    """
    Estrategia para procesar actualizaciones de estado. Asume que las actualizaciones de estado se reciben como diccionarios.
    """
    
    async def process(self, status: Dict[str, Any]):
        """
        Procesa una actualización de estado.
        
        Args:
            status (Dict[str, Any]): La actualización de estado a procesar.
        """
        print(f"Actualización de estado recibida: {status.get('status')}")

# Mapeo de tipos de cambio a estrategias para facilitar el manejo de diferentes tipos de datos.
strategies = {
    "messages": MessageProcessingStrategy(),
    "statuses": StatusUpdateProcessingStrategy(),
    "media": MediaProcessingStrategy(),
}
