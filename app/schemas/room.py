from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
import sqlalchemy.orm
from uuid import UUID
from typing import Optional
from app.models.room import Role
class RoomCreate(BaseModel):
    name: str = Field(...,min_length=1,max_length=20)
    description: Optional[str] = None
class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    profile_url: Optional[str] =None
    profile_id: Optional[str] = None
    created_at: datetime
    created_by: UUID
    model_config = ConfigDict(from_attributes=True) #SQLAlchemy to Pydantc conversion

class AddRoomMember(BaseModel):
    user_id: UUID
    role: Role = Role.MEMBER
class UserOut(BaseModel):
    id: UUID
    name: str
    profile_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    

class RoomMemberResponse(BaseModel):
    room_id: UUID
    role: Role
    joined_at: datetime
    user: UserOut
    model_config = ConfigDict(from_attributes=True)



