import os
import requests
import asyncio
import logging
import aiofiles
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from models import SendMessageRequest, IncomingMessage, SendMessageTemplateRequest, Component, EmailSchema, EmailRecipient
from config import Config
import httpx
from httpx import HTTPError, AsyncClient, HTTPStatusError, ConnectTimeout
from typing import Optional
from fastapi import Body
from subscriptions import send_event_notification
from mailjet_rest import Client
import mailjet_rest

router = APIRouter()

class AsyncHTTPClient:
    """
    Clase encargada de manejar las solicitudes HTTP de forma asíncrona. Es útil para realizar operaciones de red
    que no bloqueen la ejecución del programa principal mientras se esperan las respuestas de las solicitudes.

    Métodos:
        - request: Permite realizar solicitudes HTTP de cualquier tipo (GET, POST, etc.) de manera asíncrona.
    """
    @staticmethod
    async def request(method: str, url: str, **kwargs) -> httpx.Response:
        """
        Realiza una solicitud HTTP asíncrona usando los parámetros especificados.

        Args:
            method (str): El método HTTP a utilizar (por ejemplo, 'GET', 'POST').
            url (str): La URL a la que se hace la solicitud.
            **kwargs: Argumentos adicionales que se pueden pasar a la solicitud, como 'headers', 'json', etc.

        Returns:
            httpx.Response: Objeto de respuesta que incluye el estado de la solicitud, los datos de la respuesta, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            return response


def get_headers() -> dict:
    """
    Genera y retorna un diccionario de encabezados HTTP para usar en solicitudes a APIs externas, especialmente útil
    para incluir autorización y otros encabezados comunes en las solicitudes.

    Returns:
        dict: Diccionario con los encabezados configurados, incluyendo el tipo de contenido y el token de autorización.
    """
    return {
        "Content-Type": "application/json",  # Especifica el tipo de contenido que se está enviando
        "Authorization": f"Bearer {Config.USER_ACCESS_TOKEN}"  # Autenticación mediante token de acceso
    }


def get_media_file_path(media_type: str, media_id: str, extension: str, filename: Optional[str] = None) -> str:
    """
    Genera y retorna la ruta del archivo donde se guardará un medio específico. Esto es útil para organizar los archivos
    descargados o generados por el sistema según su tipo y ID único, permitiendo una fácil recuperación posteriormente.

    Args:
        media_type (str): El tipo de medio (por ejemplo, 'imagen', 'video').
        media_id (str): El ID único del medio, utilizado para generar una ruta única si no se proporciona un nombre de archivo.
        extension (str): La extensión del archivo basada en su MIME type.
        filename (Optional[str]): Un nombre de archivo opcional. Si no se proporciona, se genera uno automáticamente.

    Returns:
        str: La ruta completa del archivo donde se guardará el medio, incluyendo el directorio base, el tipo de medio,
        y el nombre del archivo (ya sea proporcionado o generado).
    """
    file_path = f"./media/{media_type}/{filename or f'{media_id}.{extension}'}"  # Ruta dinámica basada en los parámetros
    return file_path


@router.post("/send-message")
async def send_message(message_request: SendMessageRequest):
    """
    Endpoint para enviar un mensaje a través de la API de WhatsApp.

    Este endpoint asincrónico acepta solicitudes POST para enviar mensajes de texto a través de
    la API de WhatsApp, utilizando las configuraciones definidas en `Config`. Este método demuestra
    cómo interactuar con APIs externas de manera asincrónica para enviar mensajes, mejorando el rendimiento
    y la escalabilidad de aplicaciones web o servicios.

    Args:
        message_request (SendMessageRequest): Un objeto de tipo SendMessageRequest que contiene la información
                                               necesaria para enviar el mensaje. Incluye el número del destinatario
                                               y el cuerpo del mensaje.

    Returns:
        dict: Un diccionario que indica el éxito del envío del mensaje, incluyendo un mensaje de estado.

    El proceso comienza registrando la intención de enviar un mensaje, seguido por la preparación y envío de la
    solicitud POST a la API de WhatsApp. Se manejan las respuestas de la API para confirmar el éxito del envío
    o para capturar y manejar errores en caso de que la solicitud no se complete satisfactoriamente.
    """
    # Registro inicial para indicar el comienzo del proceso de envío.
    logging.info(f"Sending message to recipient_number: {message_request.recipient_number}")
    
    try:
        # Envío de la solicitud POST a la API de WhatsApp.
        response = await AsyncHTTPClient.request(
            "POST",
            url=f"https://graph.facebook.com/{Config.VERSION}/{Config.PHONE_NUMBER_ID}/messages",
            headers=get_headers(),
            json={
                "messaging_product": "whatsapp", 
                "to": message_request.recipient_number, 
                "type": "text", 
                "text": {"body": message_request.message}
            },
        )
        response.raise_for_status()  # Asegura manejar respuestas HTTP no exitosas adecuadamente.

        # Registro de éxito al enviar el mensaje.
        logging.info("Message sent successfully")
        return {"status": "success", "message": "Message sent"}
    except HTTPError as http_err:
        # Captura y manejo de errores relacionados con la solicitud HTTP.
        logging.error(f"Failed to send message, status code: {http_err.response.status_code}")
        raise HTTPException(status_code=http_err.response.status_code, detail="Failed to send message")
    except Exception as err:
        # Manejo de cualquier otro tipo de error no capturado específicamente.
        logging.error(f"An unexpected error occurred while sending the message: {err}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    
@router.post("/send-template-message", response_model=dict, status_code=status.HTTP_200_OK, summary="Enviar mensaje basado en template", description="Este endpoint permite enviar un mensaje basado en template a través de WhatsApp.")
async def send_template_message(request: SendMessageTemplateRequest = Body(..., example={
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "recipient_number": "18493445928",
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": "Hola Mundo"
                    }
                ]
            }
        ]
    }
})):
    """
    Envía un mensaje basado en template a través de WhatsApp.
    
    - **messaging_product**: Producto de mensajería (ej. whatsapp).
    - **recipient_type**: Tipo de destinatario (ej. individual).
    - **recipient_number**: Número del destinatario.
    - **type**: Tipo de mensaje (template).
    - **template**: Datos del template del mensaje.

    Returns:
        dict: Un diccionario que indica el éxito del envío del mensaje, incluyendo un mensaje de estado.
    """
    try:
        async with AsyncClient() as client:
            response = await client.post(
                url=f"https://graph.facebook.com/{Config.VERSION}/{Config.PHONE_NUMBER_ID}/messages",
                headers=get_headers(),
                json={
                    "messaging_product": request.messaging_product,
                    "recipient_type": request.recipient_type,
                    "to": request.to,
                    "type": request.type,
                    "template": {
                        "name": request.template.name,
                        "language": request.template.language,
                        "components": [
                            {
                                "type": component.type,
                                "parameters": [param.model_dump(exclude_none=True) for param in component.parameters]
                            } for component in request.template.components
                        ]
                    },
                },
            )
            response.raise_for_status()
            return {"success": True, "message": "Mensaje enviado con éxito."}
    except HTTPStatusError as http_exc:
        # Error específico de respuestas HTTP no exitosas
        detail = f"HTTP error: status {http_exc.response.status_code}"
        raise HTTPException(status_code=http_exc.response.status_code, detail=detail)
    except Exception as exc:
        # Para cualquier otro tipo de error no capturado específicamente
        detail = "Error inesperado al enviar el mensaje."
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
async def get_media_url(media_id: str) -> Optional[str]:
    """
    Obtiene la URL de descarga de un medio específico utilizando su identificador único (media_id).
    
    Esta función asincrónica realiza una solicitud HTTP GET a una API externa, en este caso, la API de 
    Facebook Graph, para recuperar la URL de un medio. La naturaleza asincrónica permite que la
    ejecución de la aplicación continúe sin bloquearse mientras espera la respuesta de la red, mejorando
    la eficiencia y la capacidad de respuesta de la aplicación.
    
    Args:
        media_id (str): El identificador único del medio para el cual se desea obtener la URL.
    
    Returns:
        Optional[str]: La URL del medio si se encuentra y se recupera con éxito; None en caso contrario.
    
    Esta función es crucial para operaciones que requieren acceso a medios almacenados externamente,
    permitiendo una integración fluida con servicios de terceros y la manipulación de medios basada en
    sus URLs.
    """
    
    # Registro del intento de recuperación de la URL del medio.
    logging.info(f"Fetching media URL for media_id: {media_id}")
    
    try:
        # Realización de la solicitud HTTP GET a la API de Facebook Graph.
        response = await AsyncHTTPClient.request(
            "GET",
            f"https://graph.facebook.com/v18.0/{media_id}",  # La URL y versión de la API pueden variar.
            headers=get_headers()  # Obtención de las cabeceras necesarias para la solicitud, como tokens de autenticación.
        )
        response.raise_for_status()  # Asegura lanzar una excepción para respuestas HTTP no exitosas.

        # Registro de éxito y extracción de la URL del medio desde la respuesta.
        logging.info("Media URL fetched successfully")
        media_url = response.json().get('url')  # Extracción de la URL del medio desde el JSON de respuesta.
        return media_url
    except Exception as e:
        # Manejo de errores durante la recuperación de la URL, incluyendo errores de red y respuestas HTTP no exitosas.
        logging.error(f"Failed to obtain media URL, status code: {response.status_code}, error: {e}")
        return None


async def save_media(media_url: str, media_type: str, media_id: str, mime_type: str, filename: Optional[str] = None) -> Optional[str]:
    """p
    Descarga y guarda un medio (como imágenes, videos, etc.) localmente usando su URL.
    
    Este método asincrónico asegura que la descarga y almacenamiento del medio no bloqueen el procesamiento
    principal de la aplicación, mejorando así el rendimiento y la escalabilidad del servicio.
    
    Args:
        media_url (str): La URL desde donde se descargará el medio. Es esencial que esta URL sea accesible.
        media_type (str): El tipo de medio a descargar (por ejemplo, 'image', 'video'). Esta información puede ser
                          utilizada para clasificar los medios o aplicar lógicas específicas de procesamiento.
        media_id (str): Un identificador único para el medio. Este ID es utilizado para nombrar el archivo guardado
                        si no se proporciona un nombre de archivo específico.
        mime_type (str): El tipo MIME del medio, utilizado para determinar la extensión del archivo basándose en
                         su tipo MIME real.
        filename (Optional[str]): Un nombre de archivo opcional para el medio. Si se omite, se generará uno basado
                                   en el media_id y el tipo MIME.

    Returns:
        Optional[str]: La ruta al archivo donde se guardó el medio en caso de éxito; None en caso contrario.

    El método primero verifica la validez de la URL del medio. Luego, procede a la descarga y guarda el archivo
    en un directorio específico basado en su tipo. Se emplea manejo de excepciones para capturar y registrar
    cualquier error que pueda ocurrir durante el proceso.
    """
    # Registro de inicio de la operación de guardado.
    logging.info(f"Saving media, media_id: {media_id}, media_type: {media_type}")
    
    # Verificación de la URL del medio proporcionada.
    if not media_url:
        logging.warning(f"No media URL provided for media_id: {media_id}")
        return None

    # Limpieza y obtención de la extensión del archivo basada en el tipo MIME.
    clean_mime_type = mime_type.split(';')[0]
    extension = clean_mime_type.split('/')[-1]
    
    # Generación de la ruta del archivo donde se guardará el medio.
    file_path = get_media_file_path(media_type, media_id, extension, filename)

    try:
        # Realización de la solicitud HTTP para descargar el medio.
        response = await AsyncHTTPClient.request("GET", media_url, headers=get_headers())
        response.raise_for_status()  # Asegura manejar respuestas HTTP no exitosas.
        
        # Creación del directorio si no existe y apertura del archivo para escribir el contenido del medio.
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(response.content)
        logging.info(f"Media downloaded and saved at: {file_path}")
        return file_path
    except Exception as e:
        # Registro de cualquier error ocurrido durante la descarga o el guardado del medio.
        logging.error(f"Failed to download media for media_id: {media_id}, status code: {response.status_code}, error: {e}")
        return None

# Las demás funciones permanecen sin cambios significativos en su lógica interna.
# Se debe adaptar el uso de AsyncHTTPClient donde sea necesario y aplicar la generación de rutas de archivos con `get_media_file_path`.

# Esta refactorización centraliza el manejo de solicitudes HTTP y la generación de rutas de archivos,
# siguiendo las sugerencias de mejoras generales y específicas.
async def handle_media_message(media_id: str, media_type: str, mime_type: str, filename: Optional[str] = None, caption: Optional[str] = None):
    """
    Maneja de manera asíncrona el procesamiento de un mensaje de medios, como imágenes o videos. Esta función es
    responsable de obtener la URL del medio basada en su ID, y luego proceder a guardar el medio localmente en el
    servidor. Se puede especificar un nombre de archivo y un subtítulo opcional para el medio.

    Args:
        media_id (str): Identificador único del medio que se va a procesar. Este ID se usa para obtener la URL del
                        medio desde el servicio externo o base de datos.
        media_type (str): Indica el tipo de medio (por ejemplo, 'imagen', 'video'). Esta información puede ser
                          utilizada para procesar el medio de manera adecuada o para decidir su destino final.
        mime_type (str): Tipo MIME del medio, que proporciona información sobre el formato del archivo. Esto es útil
                         para determinar cómo manipular o visualizar el medio.
        filename (Optional[str]): Nombre de archivo personalizado para guardar el medio. Si no se proporciona, se
                                  puede generar un nombre basado en el media_id o cualquier otra lógica definida.
        caption (Optional[str]): Subtítulo o descripción asociada con el medio. Este podría ser utilizado para
                                 almacenamiento adicional o metadatos.

    Esta función intenta primero obtener la URL del medio y, si tiene éxito, procede a guardar el medio localmente.
    Se registra cada paso del proceso, facilitando el seguimiento y la depuración.
    """
    try:
        # Registro de inicio del procesamiento para seguimiento y depuración.
        logging.info(f"Processing media message: {media_id}")

        # Obtención de la URL del medio basado en su ID. Es necesario manejar fallos en este punto
        # ya que podría indicar problemas de conectividad o IDs incorrectos.
        media_url = await get_media_url(media_id)
        if media_url:
            # Si la URL se obtiene con éxito, proceder a guardar el medio localmente.
            file_path = await save_media(media_url, media_type, media_id, mime_type, filename)
            if file_path:
                # Confirmación del guardado exitoso del medio para registro y seguimiento.
                logging.info(f"Media saved successfully at {file_path}")
                # Este es un buen lugar para realizar operaciones adicionales, como actualizaciones en base de datos.
            else:
                # Manejo y registro de errores en caso de fallo al guardar el medio.
                logging.error(f"Failed to save media for media_id: {media_id}. The file_path was not obtained.")
        else:
            # Registro de errores en caso de no poder obtener la URL del medio, lo cual es crítico para el proceso.
            logging.error(f"Failed to fetch media URL for media_id: {media_id}. Check if the media_id is correct and the media is accessible.")
    except Exception as e:
        # Manejo general de excepciones para asegurar que cualquier error inesperado sea registrado adecuadamente.
        logging.error(f"An error occurred while processing media message {media_id}: {e}")
        # La decisión de lanzar la excepción o manejarla de manera silenciosa dependerá del flujo específico de la aplicación y de la criticidad del proceso de manejo de medios.



async def process_message(message):
    """
    Procesa de manera asíncrona un mensaje individual recibido a través del webhook.
    Esta función está diseñada para manejar diferentes tipos de mensajes, enfocándose específicamente en mensajes
    que contienen medios, como imágenes, videos, etc., extrayendo información relevante e iniciando pasos de
    procesamiento adicionales.

    Args:
        message: Un objeto que representa el mensaje recibido. Se espera que este objeto tenga varios atributos
                 dependiendo de su tipo (por ejemplo, texto, imagen, video), incluyendo, pero no limitado a, un ID
                 para medios, tipo MIME, nombre de archivo y subtítulo.

    La función emplea programación defensiva inicializando variables de antemano para evitar errores de referencia.
    También maneja excepciones de manera elegante para asegurar que un mensaje fallido no interrumpa el flujo de
    procesamiento general.
    """
    try:
        # Inicializar variables para asegurar que están definidas incluso si no son establecidas por el mensaje.
        # Esto previene errores de referencia durante las verificaciones condicionales y el procesamiento.
        media_id = None
        mime_type = None
        filename = None
        caption = None

        # Verificar si el objeto mensaje tiene un atributo nombrado según su tipo (por ejemplo, 'image', 'video')
        # y extraer información relevante si está presente.
        if hasattr(message, message.type):
            media_section = getattr(message, message.type)
            media_id = getattr(media_section, 'id', None)
            mime_type = getattr(media_section, 'mime_type', '').split("/")[-1] if hasattr(media_section, 'mime_type') else None
            filename = getattr(media_section, 'filename', None)
            caption = getattr(media_section, 'caption', None)

        # Proceder con el procesamiento si se presenta un ID de medio, indicando un mensaje de medio.
        if media_id:
            logging.info(f"Procesando mensaje de tipo '{message.type}' con media_id '{media_id}'")
            await handle_media_message(media_id, message.type, mime_type, filename, caption)
        else:
            # Registrar una advertencia si no se encuentra un ID de medio, indicando que el mensaje puede no requerir
            # procesamiento o no ser compatible con la lógica actual.
            logging.warning(f"Mensaje recibido sin media_id. Tipo de mensaje: '{message.type}'")
    except Exception as e:
        # Registrar cualquier excepción encontrada durante el procesamiento del mensaje.
        # Esto ayuda a identificar problemas sin detener el procesamiento de mensajes subsiguientes.
        logging.error(f"Error al procesar mensaje: {e}")
        # Dependiendo de las necesidades de la aplicación, podrías querer volver a lanzar excepciones o manejarlas
        # de manera silenciosa. Esta decisión debe basarse en la criticidad de procesar cada mensaje con éxito.


@router.post("/webhook", status_code=200)
async def receive_message(request: IncomingMessage):
    """
    Este método actúa como el punto de entrada para los mensajes entrantes a través del webhook.
    Es invocado por un sistema externo (e.g., WhatsApp Business API) cuando se reciben nuevos mensajes o eventos.
    
    La función está diseñada para ser asincrónica, lo que permite manejar múltiples mensajes de manera eficiente
    sin bloquear el servidor, mejorando así la escalabilidad de la aplicación.

    Args:
        request (IncomingMessage): Un objeto IncomingMessage que contiene los detalles del mensaje entrante,
                                   conforme al modelo Pydantic definido. Este objeto facilita la validación y el manejo
                                   de los datos recibidos.

    Returns:
        JSONResponse: Una respuesta HTTP indicando el resultado del procesamiento del mensaje. Devuelve un estado
                      de éxito junto con un mensaje correspondiente en caso de éxito, o un estado de error en caso de fallo.
    """
    try:
        # Conversión del cuerpo de la solicitud a un diccionario para facilitar el registro y la depuración.
        # Es importante asegurar que el modelo IncomingMessage tenga un método 'dict()' para esta conversión.
        request_data = request.model_dump()
        logging.info(f"Evento recibido: {request_data}")

        # Lista para acumular tareas asincrónicas correspondientes al procesamiento de cada mensaje.
        tasks = []

        # Iteración a través de cada entrada en el mensaje recibido. Cada 'entry' puede representar
        # diferentes mensajes o eventos que necesitan ser procesados.
        for entry in request.entry:
            for change in entry.changes:
                # Verificación de la presencia de mensajes en el cambio actual para procesar.
                if change.value.messages:
                    # Programación de una tarea asincrónica para cada mensaje encontrado.
                    # Esto permite un procesamiento concurrente y eficiente de múltiples mensajes.
                    for message in change.value.messages:
                        tasks.append(process_message(message))
                elif change.value.statuses:
                    for statuses in change.value.statuses:
                        logging.info(f"Actualización de estado: {statuses.status}")

        # Si hay tareas programadas, se ejecutan de manera concurrente.
        # Esto es crucial para mantener la eficiencia y la capacidad de respuesta del servicio.
        if tasks:
            await asyncio.gather(*tasks)
            logging.info("Todas las tareas procesadas con éxito.")

        await send_event_notification(request)

        # Respuesta exitosa tras el procesamiento de los mensajes.
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "message": "Evento procesado con éxito"})
    except ConnectTimeout as e:
        logging.error("Connection timeout")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"status": "error", "message": "Timeout de conexión"})
    except HTTPStatusError as e:
        logging.error(f"Ha ocurrido un error no manejado: {e.response.status_code}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": "Error, favor tomar nota de la actividad enviada y comunicarse con el supldior"})
    except Exception as e:
        # Registro de cualquier excepción ocurrida durante el procesamiento.
        # Es importante capturar y registrar excepciones para facilitar la depuración y mantenimiento.
        logging.error(f"Error al procesar el mensaje: {e}")

        # Respuesta indicando fallo en el procesamiento debido a la excepción capturada.
        # Devolver un mensaje de error específico puede ayudar en la identificación rápida del problema.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Error al procesar evento"})

def build_email_recipients_list(recipients):
    return [{"Email": r.email, "Name": r.name} if isinstance(r, EmailRecipient) else {"Email": r, "Name": r.split('@')[0]} for r in recipients]

@router.post("/send-email")
def send_email(email_data: EmailSchema):
    try:
        mailjet = Client(auth=(Config.MAILJET_KEY, Config.MAILJET_SECRET), version='v3.1')
        # Transforma cada entrada a la estructura adecuada

        message = {
            "From": {
                "Email": email_data.from_email,
                "Name": email_data.from_name
            },
            "To": build_email_recipients_list(email_data.to_emails),
            "Subject": email_data.subject,
            "TextPart": email_data.text_part,
            "HTMLPart": email_data.html_part,
            "CustomID": "AppGettingStartedTest"
        }

        if email_data.cc:
            message["Cc"] = build_email_recipients_list(email_data.cc)

        if email_data.bcc:
            message["Bcc"] = build_email_recipients_list(email_data.bcc)

        data = {"Messages": [message]}

            
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            return {"message": "Email sent successfully"}
        else:
            # Log this error
            logging.error(f"Fallo al enviar el correo: {result.json()}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Email failed to send", "details": result.json()}
            )
    except Exception as e:
        # Log this error
        logging.error(f"Ha ocurrido un error no manejado: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred", "details": str(e)}
        )  