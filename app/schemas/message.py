from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class CreateMessage(BaseModel):
    media_url: Optional[str]
    content: str
class Sender(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)
class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID
    sender: Sender
    media_url: Optional[str]
    content: str
    posted_at:datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


