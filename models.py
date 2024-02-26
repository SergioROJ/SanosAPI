from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Revisión de los Modelos Pydantic

class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class Conversation(BaseModel):
    id: str
    origin: Optional[Dict[str, Any]] = None
    expiration_timestamp: Optional[int] = None

class Pricing(BaseModel):
    billable: bool
    pricing_model: str
    category: str

class Status(BaseModel):
    id: str
    status: str
    timestamp: int
    recipient_id: str
    conversation: Conversation
    pricing: Pricing

class Media(BaseModel):
    mime_type: str
    sha256: str
    id: str
    caption: Optional[str] = None  # Asegúrate de que este campo sea opcional si no siempre se proporciona

class Image(Media):
    pass  # Sin cambios específicos requeridos

class Audio(Media):
    pass  # Sin cambios específicos requeridos

class Video(Media):
    pass  # Sin cambios específicos requeridos

class Document(Media):
    filename: str  # Asegúrate de que este campo siempre se proporcione para documentos

class Text(BaseModel):
    body: Optional[str] = None

class Message(BaseModel):
    from_: str = Field(..., alias='from')  # Asegúrate de que el alias se maneje correctamente
    id: str
    timestamp: int
    type: str
    text: Optional[Text] = None
    image: Optional[Image] = None
    audio: Optional[Audio] = None
    video: Optional[Video] = None
    document: Optional[Document] = None

class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str

class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[Status]] = None

class Change(BaseModel):
    value: Value
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class IncomingMessage(BaseModel):
    object: str
    entry: List[Entry]

class SendMessageRequest(BaseModel):
    recipient_number: str
    message: str
