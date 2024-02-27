import os
import requests
import asyncio
import logging
import aiofiles
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from models import SendMessageRequest, IncomingMessage
from config import Config
from httpx import AsyncClient
from typing import Optional

router = APIRouter()

def get_headers() -> dict:
    """
    Genera y retorna un diccionario de encabezados para usar en las solicitudes HTTP.
    Esto es necesario para incluir el tipo de contenido y el token de autorización en cada solicitud.

    Returns:
        dict: Un diccionario conteniendo los encabezados requeridos para las solicitudes.
    """
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}"
    }

@router.post("/send-message")
async def send_message(message_request: SendMessageRequest):
    """
    Endpoint para enviar un mensaje a través de la API de WhatsApp.
    
    Args:
        message_request (SendMessageRequest): El cuerpo de la solicitud que contiene el número del destinatario y el mensaje a enviar.

    Returns:
        dict: Un diccionario con el estado de la operación y un mensaje correspondiente.
    
    Raises:
        HTTPException: Si la solicitud a la API de WhatsApp falla.
    """
    logging.info(f"Sending message to recipient_number: {message_request.recipient_number}")
    async with AsyncClient() as client:
        response = await client.post(
            url=f"https://graph.facebook.com/{Config.VERSION}/{Config.PHONE_NUMBER_ID}/messages",
            headers=get_headers(),
            json={"messaging_product": "whatsapp", "to": message_request.recipient_number, "type": "text", "text": {"body": message_request.message}},
        )
        if response.status_code == 200:
            logging.info("Message sent successfully")
            return {"status": "success", "message": "Message sent"}
        else:
            logging.error(f"Failed to send message, status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send message")

async def get_media_url(media_id: str) -> Optional[str]:
    """
    Obtiene la URL de un medio a través de su ID haciendo una solicitud a la API de Facebook.
    
    Args:
        media_id (str): El ID del medio cuya URL se desea obtener.

    Returns:
        Optional[str]: La URL del medio si la solicitud es exitosa; None de lo contrario.
    """
    logging.info(f"Fetching media URL for media_id: {media_id}")
    async with AsyncClient() as client:
        response = await client.get(f"https://graph.facebook.com/v18.0/{media_id}", headers=get_headers())
        if response.status_code == 200:
            logging.info("Media URL fetched successfully")
            media_url = response.json().get('url')
            return media_url
        else:
            logging.error(f"Failed to obtain media URL, status code: {response.status_code}")
            return None

async def save_media(media_url: str, media_type: str, media_id: str, mime_type: str, filename: Optional[str] = None) -> Optional[str]:
    """
    Descarga y guarda un medio (imagen, video, etc.) localmente usando su URL.
    
    Args:
        media_url (str): URL del medio a descargar.
        media_type (str): Tipo de medio (por ejemplo, 'image', 'video').
        media_id (str): ID del medio, utilizado para nombrar el archivo si no se proporciona un nombre específico.
        mime_type (str): Tipo MIME del medio, utilizado para determinar la extensión del archivo.
        filename (Optional[str]): Nombre opcional para el archivo a guardar. Si no se proporciona, se genera uno.

    Returns:
        Optional[str]: La ruta del archivo donde se guardó el medio si la descarga es exitosa; None de lo contrario.
    """
    logging.info(f"Saving media, media_id: {media_id}, media_type: {media_type}")
    if not media_url:
        logging.warning(f"No media URL provided for media_id: {media_id}")
        return None

    clean_mime_type = mime_type.split(';')[0]
    extension = clean_mime_type.split('/')[-1]
    file_path = f"./media/{media_type}/{filename or f'{media_id}.{extension}'}"

    async with AsyncClient() as client:
        response = await client.get(media_url, headers=get_headers())
        if response.status_code == 200:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            async with aiofiles.open(file_path, 'wb') as file:
                await file.write(response.content)
            logging.info(f"Media downloaded and saved at: {file_path}")
            return file_path
        else:
            logging.error(f"Failed to download media for media_id: {media_id}, status code: {response.status_code}")
            return None

async def handle_media_message(media_id: str, media_type: str, mime_type: str, filename: Optional[str] = None, caption: Optional[str] = None):
    """
    Procesa un mensaje que contiene un medio, obteniendo su URL y guardándolo localmente.
    
    Args:
        media_id (str): ID del medio a procesar.
        media_type (str): Tipo de medio (imagen, video, etc.).
        mime_type (str): Tipo MIME del medio.
        filename (Optional[str]): Nombre opcional para el archivo a guardar.
        caption (Optional[str]): Subtítulo opcional asociado con el medio.
    """
    logging.info(f"Processing media message: {media_id}")
    media_url = await get_media_url(media_id)
    if media_url:
        file_path = await save_media(media_url, media_type, media_id, mime_type, filename)
        if file_path:
            logging.info(f"Media saved successfully at {file_path}")
            # Aquí puedes realizar operaciones adicionales, como actualizar una base de datos con la información del medio guardado
        else:
            logging.warning(f"Failed to save media for media_id: {media_id}")
    else:
        logging.warning(f"Failed to fetch media URL for media_id: {media_id}")

async def process_message(message: dict):
    """
    Procesa un mensaje entrante, manejando tanto mensajes de texto como mensajes con medios.
    
    Args:
        message (dict): El mensaje a procesar, obtenido del webhook de mensajes entrantes.
    """
    # Aquí deberías implementar la lógica para procesar el mensaje, por ejemplo:
    # - Extraer la información necesaria del mensaje
    # - Llamar a handle_media_message si el mensaje contiene un medio
    # - Guardar el mensaje en una base de datos, si es necesario
    pass

@router.post("/webhook", status_code=200)
async def webhook(data: IncomingMessage):
    """
    Endpoint que recibe notificaciones de mensajes entrantes a través del webhook configurado.
    
    Args:
        data (IncomingMessage): El cuerpo de la solicitud, conteniendo los mensajes entrantes.

    Returns:
        JSONResponse: Respuesta indicando el éxito de la recepción del mensaje.
    """
    logging.info("Received webhook notification")
    try:
        # Asumiendo que data.entries contiene los mensajes entrantes
        # Esta sección debe ser adaptada según la estructura exacta de los datos recibidos
        tasks = [process_message(message) for entry in data.entries for message in entry.messages]
        await asyncio.gather(*tasks)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "success", "message": "Messages processed"})
    except Exception as e:
        logging.error(f"Error processing messages: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": "error", "message": "Failed to process messages"})
