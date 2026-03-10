from app.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy import String, DateTime, func,ForeignKey,UniqueConstraint
from datetime import datetime
from typing import Optional
from sqlalchemy import Enum as SQLEnum
from enum import Enum

class Role(str,Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default= uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    profile_url: Mapped[Optional[str]] = mapped_column(String,nullable=True)
    profile_id: Mapped[Optional[str]] = mapped_column(String,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable= False
    )
    messages = relationship("Message",back_populates="room")
    #items = relationship("RoomMember", cascade="all, delete-orphan")

class RoomMember(Base):
    __tablename__ = "room_members"
    __table_args__ = (
        UniqueConstraint("user_id", "room_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default= uuid.uuid4,

    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id")
    )

    joined_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),nullable=False)

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, native_enum = False),
        nullable=False
    )
    user = relationship("User", back_populates="rooms")

