from abc import ABC, abstractmethod
from typing import Dict, Any
from models import Message  # Asegúrate de que esta importación sea correcta según tu estructura de proyecto
import routes

class ProcessingStrategy(ABC):
    @abstractmethod
    async def process(self, data: Any):  # Cambiado Dict[str, Any] por Any para permitir objetos Pydantic
        pass

class MessageProcessingStrategy(ProcessingStrategy):
    async def process(self, message: Message):  # Cambiado el tipo de Dict a Message para reflejar el modelo Pydantic
        # Implementación ajustada para trabajar directamente con el modelo Pydantic
        print(f"Mensaje recibido: {message.text.body if message.text else 'No body'}")

class MediaProcessingStrategy(ProcessingStrategy):
    async def process(self, message: Message):
        if message.type == 'image' and message.image:
            media_id = message.image.id
            # Aquí podrías llamar a una función para manejar la descarga y el almacenamiento
            # basado en el media_id y el tipo de medio
            print(f"Descargando imagen con media_id: {media_id}")
            # Por ejemplo:
            #await save_media(media_id, "pictures")
        elif message.type == 'voice' and message.voice:
            media_id = message.voice.id
            print(f"Descargando voz con media_id: {media_id}")
            #await save_media(media_id, "voice")
        elif message.type == 'video' and message.video:
            media_id = message.video.id
            print(f"Descargando video con media_id: {media_id}")
            #await save_media(media_id, "video")
        else:
            print("Tipo de mensaje no manejado por esta estrategia.")

class StatusUpdateProcessingStrategy(ProcessingStrategy):
    async def process(self, status: Dict[str, Any]):
        # Asumiendo que status sigue siendo un diccionario
        print(f"Actualización de estado recibida: {status.get('status')}")

# Mapeo de tipos de cambio a estrategias sigue igual
strategies = {
    "messages": MessageProcessingStrategy(),
    "statuses": StatusUpdateProcessingStrategy(),
    "media": MediaProcessingStrategy(),
}