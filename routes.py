import os
import requests
import asyncio
import logging
import aiofiles
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from models import SendMessageRequest, IncomingMessage, Message
from strategies import strategies
from config import Config
from httpx import AsyncClient
from typing import Optional

router = APIRouter()

@router.post("/send-message")
async def send_message(message_request: SendMessageRequest):
    logging.info("Sending message to recipient_number: %s", message_request.recipient_number)
    async with AsyncClient() as client:
        response = await client.post(
            url=f"https://graph.facebook.com/{Config.VERSION}/{Config.PHONE_NUMBER_ID}/messages",
            headers={"Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": message_request.recipient_number, "type": "text", "text": {"body": message_request.message}},
        )
        if response.status_code == 200:
            logging.info("Message sent successfully")
            return {"status": "success", "message": "Message sent"}
        else:
            logging.error("Failed to send message, status code: %d", response.status_code)
            raise HTTPException(status_code=response.status_code, detail="Failed to send message")

async def get_media_url(media_id: str) -> str:
    logging.info("Fetching media URL for media_id: %s", media_id)
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {
        "Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}"
    }
    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            # Suponiendo que la respuesta incluya una URL directa al archivo multimedia
            logging.info("Media URL fetched successfully")
            media_url = response.json().get('url')
            return media_url
        else:
            logging.error("Failed to obtain media URL, status code: %d", response.status_code)
            raise HTTPException(status_code=response.status_code, detail="Failed to obtain media URL")
        
async def save_media(media_url: str, media_type: str, media_id: str, mime_type: str, filename: Optional[str] = None):
    logging.info("Saving media, media_id: %s, media_type: %s", media_id, media_type)
    headers = {
        "Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}"
    }
    if media_url:
        if media_type == 'document':
            file_path = f"./media/{media_type}/{filename}"
        else:
            file_path = f"./media/{media_type}/{media_id}.{mime_type}"
        logging.info("Media is downloading at: %s", file_path)

        async with AsyncClient() as client:
            logging.info("Request is being made at: %s", media_url)
            response = await client.get(media_url, headers=headers)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                async with aiofiles.open(file_path, 'wb') as file:
                    await file.write(response.content)
                return file_path
    else:
        logging.warning("Failed to save media for media_id: %s", media_id)
    return None

async def handle_image_message(media_id: str, media_type: str, mime_type: str, filename: Optional[str] = None):
    logging.info(f"Processing media message: {media_id}")
    media_url = await get_media_url(media_id)  # Asegúrate de pasar el access_token aquí
    if media_url and media_type != 'document':
        await save_media(media_url, media_type, media_id, mime_type)
    elif media_url and media_type == 'document':
        await save_media(media_url, media_type, media_id, mime_type, filename)
    else:
        logging.error(f"Failed to process image message: {media_id}")

@router.post("/webhook")
async def receive_message(request: IncomingMessage):
    request_data = request.model_dump_json()
    logging.info("Received event: %s", request_data)
    
    tasks = []
    for entry in request.entry:
        for change in entry.changes:
            # Asumiendo que todos los cambios son mensajes por ahora
            for message in change.value.messages:  # Accediendo directamente a los mensajes
                if message.type == 'image':
                    # Procesar mensaje de imagen
                    logging.info(f"Processing image message: {message.image.id}")
                    media_id = message.image.id
                    tasks.append(handle_image_message(media_id, "pictures", message.image.mime_type.split("/")[-1]))
                elif message.type == 'text':
                    #procesar mensaje de texto
                    logging.info(f"El mensaje recibido es: {message.text.body}")
                elif message.type == 'audio':
                    #Procesar mensaje nota de voz
                    logging.info(f"Processing audio message: {message.audio.id}")
                    media_id = message.audio.id
                    tasks.append(handle_image_message(media_id, "voice", message.audio.mime_type.split("/")[-1].split(";")[0]))
                elif message.type == 'video':
                    #Procesar mensaje de video
                    logging.info(f"Processing image message: {message.video.id}")
                    media_id = message.video.id
                    tasks.append(handle_image_message(media_id, "video", message.video.mime_type.split("/")[-1]))
                elif message.type == 'document':
                    logging.info(f"Processing document message: {message.document.id}")
                    media_id = message.document.id
                    tasks.append(handle_image_message(media_id, "document", message.document.filename.split(".")[-1], message.document.filename))
                else:
                    logging.info(f"Unhandled message type: {message.type}")

    if tasks:
        await asyncio.gather(*tasks)
        logging.info("All tasks processed successfully.")
    else:
        logging.info("No tasks to process.")

    return JSONResponse(content={"status": "success", "message": "Event processed successfully"}, status_code=status.HTTP_200_OK)