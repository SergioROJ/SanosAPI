from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import WebhookRegistrationRequest, IncomingMessage
import httpx
import logging

app = FastAPI()

# Este diccionario es solo para fines de demostración. En producción, deberías almacenar esto en una base de datos.
webhook_subscriptions = {"https://0e6f-2001-1308-2d10-d000-6180-9312-ea7e-92ef.ngrok-free.app/webhook"}

# Definir validate_webhook para realizar la validación
async def validate_webhook(url: str):
    try:
        # Simulamos una solicitud de verificación a la URL del webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"message": "Verificación del webhook"})
            if response.status_code != 200:
                raise ValueError("Validación del webhook fallida")
    except (httpx.RequestError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/register-webhook/")
async def register_webhook(request: WebhookRegistrationRequest):
    # Verificar si el webhook ya está registrado
    if request.url in webhook_subscriptions:
        raise HTTPException(status_code=400, detail="Webhook ya registrado")
    
    # Validar la URL del webhook antes de registrarla
    await validate_webhook(request.url)
    
    # Registrar el webhook después de la validación exitosa
    webhook_subscriptions[request.url] = request.events
    return {"message": "Webhook registrado con éxito"}

async def send_event_notification(event_data: IncomingMessage):
    # Asume que tienes una lista de URLs de webhook registradas
    async with httpx.AsyncClient() as client:
        for webhook_url in webhook_subscriptions:
            try:
                # Envía la notificación del evento a cada webhook registrado
                logging.info(f"ESTA ES LA URL CLIENTE>>>>>>>>> {webhook_url}")
                await client.post(webhook_url, json=event_data.model_dump())
            except httpx.RequestError as e:
                print(f"Error al enviar notificación a {webhook_url}: {str(e)}")