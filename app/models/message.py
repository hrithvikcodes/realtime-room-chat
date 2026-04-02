from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.db import Base
from typing import Optional





class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default = uuid.uuid4,
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id"),
        nullable=False,
        index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    media_url : Mapped[Optional[str]] = mapped_column(String,nullable=True)
    media_id: Mapped[Optional[str]] = mapped_column(String,nullable=True)
    content: Mapped[str] = mapped_column(Text,nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(), onupdate=func.now(),nullable=False)
    room = relationship("Room", back_populates="messages")
    sender = relationship("User",back_populates="messages")