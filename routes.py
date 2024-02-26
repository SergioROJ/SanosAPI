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

# Asegúrate de que esta función se coloca antes de su primera utilización
def get_headers() -> dict:
    """
    Genera y retorna un diccionario de encabezados para usar en solicitudes HTTP.

    Retorna:
        dict: Un diccionario de encabezados.
    """
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}"
    }

@router.post("/send-message")
async def send_message(message_request: SendMessageRequest):
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
    logging.info(f"Saving media, media_id: {media_id}, media_type: {media_type}")
    if not media_url:
        logging.warning(f"No media URL provided for media_id: {media_id}")
        return None

    # Aquí ajustamos cómo manejar el mime_type para eliminar cualquier cosa después de ';'
    # Esto asegura que solo se usa la parte relevante del mime_type para la extensión del archivo.
    clean_mime_type = mime_type.split(';')[0]  # Solo conserva lo que está antes del ';'
    extension = clean_mime_type.split('/')[-1]  # Obtiene la extensión después del '/'

    # Usamos la extensión limpia para el nombre del archivo
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
    logging.info(f"Processing media message: {media_id}")
    media_url = await get_media_url(media_id)
    if media_url:
        file_path = await save_media(media_url, media_type, media_id, mime_type, filename)
        if file_path:
            logging.info(f"Media saved successfully at {file_path}")
        else:
            logging.error(f"Failed to save media for media_id: {media_id}")
    else:
        logging.error(f"Failed to fetch media URL for media_id: {media_id}")

    if caption:
        logging.info(f"Message contains caption: {caption}")

async def process_message(message):
    media_id = getattr(message, message.type).id if hasattr(message, message.type) else None
    mime_type = getattr(message, message.type).mime_type.split("/")[-1] if hasattr(message, message.type) else None
    filename = getattr(message, message.type).filename if hasattr(getattr(message, message.type, None), 'filename') else None
    caption = getattr(message, message.type).caption if hasattr(getattr(message, message.type, None), 'caption') else None

    if media_id:
        await handle_media_message(media_id, message.type, mime_type, filename, caption)

@router.post("/webhook")
async def receive_message(request: IncomingMessage):
    request_data = request.dict()  # Asegurarse de que 'IncomingMessage' tenga un método 'dict()' o usar una serialización adecuada
    logging.info(f"Received event: {request_data}")

    tasks = []
    for entry in request.entry:
        for change in entry.changes:
            if change.value.messages:
                for message in change.value.messages:
                    tasks.append(process_message(message))

    if tasks:
        await asyncio.gather(*tasks)
        logging.info("All tasks processed successfully.")
    return JSONResponse(content={"status": "success", "message": "Event processed successfully"}, status_code=status.HTTP_200_OK)
