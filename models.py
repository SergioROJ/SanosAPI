from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Modelos Pydantic
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Modelos Pydantic
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
    caption: str

class Image(Media):
    pass  # Aquí puedes añadir campos específicos de la imagen si los hay

class Audio(Media):
    pass  # Aquí puedes añadir campos específicos de la voz si los hay

class Video(Media):
    pass  # Aquí puedes añadir campos específicos del video si los hay

class Document(Media):
    filename: str

class Text(BaseModel):
    body: Optional[str] = None

class Message(BaseModel):
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