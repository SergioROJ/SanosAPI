from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

# ****************************************
# *                                      *
# *                                      *
# *                                      *
# *  Modelos de enrutamiento a WhatsApp  *
# *                                      *
# *                                      *
# *                                      *
# ****************************************

class Profile(BaseModel):
    """
    Representa el perfil de un contacto, con su nombre.
    """
    name: str

class Contact(BaseModel):
    """
    Define un contacto, incluyendo su perfil y WhatsApp ID.
    """
    profile: Profile
    wa_id: str

class Origin(BaseModel):
    type: str

class Conversation(BaseModel):
    """
    Información sobre una conversación, incluyendo su ID y datos opcionales de origen y expiración.
    """
    id: str
    origin: Optional[Origin] = None
    expiration_timestamp: Optional[str] = None

class Pricing(BaseModel):
    """
    Detalles sobre la facturación de un mensaje, incluyendo si es facturable, el modelo y categoría de precio.
    """
    billable: bool
    pricing_model: str
    category: str

class Statuses(BaseModel):
    """
    Estado de un mensaje, incluyendo su ID, estado, timestamp, ID del destinatario, conversación relacionada y detalles de facturación.
    """
    id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation: Optional[Conversation] = None
    pricing: Optional[Pricing] = None


class Media(BaseModel):
    """
    Representa un medio general (imagen, audio, video, documento), con su tipo MIME, hash SHA256, ID y un subtítulo opcional.
    """
    mime_type: str
    sha256: str
    id: str
    caption: Optional[str] = None

class Image(Media):
    """
    Especialización de Media para imágenes.
    """
    pass

class Audio(Media):
    """
    Especialización de Media para audios.
    """
    pass

class Video(Media):
    """
    Especialización de Media para videos.
    """
    pass

class Document(Media):
    """
    Especialización de Media para documentos, requiriendo un nombre de archivo.
    """
    filename: str

class Text(BaseModel):
    """
    Representa el cuerpo de un mensaje de texto.
    """
    body: Optional[str] = None

class Message(BaseModel):
    """
    Abstracción de un mensaje, que puede ser de texto, imagen, audio, video o documento.
    """
    from_: str = Field(..., alias='from')
    id: str
    timestamp: int
    type: str
    text: Optional[Text] = None
    image: Optional[Image] = None
    audio: Optional[Audio] = None
    video: Optional[Video] = None
    document: Optional[Document] = None

class Metadata(BaseModel):
    """
    Metadatos asociados con un mensaje, incluyendo el número de teléfono mostrado y el ID del teléfono.
    """
    display_phone_number: str
    phone_number_id: str

class Value(BaseModel):
    """
    Valores dentro de un cambio notificado, incluyendo producto de mensajería, metadatos, contactos, mensajes y estados.
    """
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[Statuses]] = None

class Change(BaseModel):
    """
    Representa un cambio notificado, conteniendo el valor del cambio y el campo afectado.
    """
    value: Value
    field: str

class Entry(BaseModel):
    """
    Entrada en la notificación de un webhook, conteniendo los cambios notificados.
    """
    id: str
    changes: List[Change]

class IncomingMessage(BaseModel):
    """
    Mensaje entrante a través de un webhook, conteniendo las entradas con los cambios notificados.
    """
    object: str
    entry: List[Entry]

class SendMessageRequest(BaseModel):
    """
    Solicitud para enviar un mensaje, incluyendo el número del destinatario y el mensaje.
    """
    recipient_number: str
    message: str

class Parameter(BaseModel):
    type: str
    text: Optional[str] = None
    currency: Optional[dict] = None
    date_time: Optional[dict] = None

class Component(BaseModel):
    type: str = "body"
    parameters: Optional[List[Parameter]] = []

class Template(BaseModel):
    name: str
    language: dict
    components: List[Component] = []

class SendMessageTemplateRequest(BaseModel):
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    to: str
    type: str = "template"
    template: Template

# ****************************************
# *                                      *
# *                                      *
# *                                      *
# *    MODELOS DE LÓGICA DE CORREOS      *
# *                                      *
# *                                      *
# *                                      *
# ****************************************

class EmailRecipient(BaseModel):
    email: EmailStr
    name: str

class EmailSchema(BaseModel):
    from_email: EmailStr
    from_name: str
    to_emails: List[EmailRecipient]
    cc: Optional[List[EmailRecipient]] = []
    bcc: Optional[List[EmailRecipient]] = []
    subject: str
    text_part: str
    html_part: str


# ****************************************
# *                                      *
# *                                      *
# *                                      *
# *    MODELOS DE LÓGICA DE NEGOCIOS    *
# *                                      *
# *                                      *
# *                                      *
# ****************************************

class WebhookRegistrationRequest(BaseModel):
    url: str
    events: list[str]  # Lista de eventos a los que el cliente desea suscribirse