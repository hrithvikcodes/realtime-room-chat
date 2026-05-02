from app.imagekit import upload_to_imagekit
from sqlalchemy import delete, insert,update, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi  import Form, UploadFile, File
from app.models.room import Room
from app.models.message import Message
from uuid import UUID
from sqlalchemy.orm import joinedload, selectinload
from app.models.user import User
from typing import Optional
from sqlalchemy.orm import selectinload
'''from app.logger import get_logger
logger = get_logger("messages.crud")'''
async def send_message(room_id:UUID,user_id:UUID,db: AsyncSession,content: str,file: Optional[UploadFile] = None):
    
    if file is not None:
        file_url, file_id = await upload_to_imagekit(file)
    else:
        file_url, file_id = None, None
    new_msg = Message(
        content= content,
        media_url = file_url,
        media_id = file_id,
        room_id = room_id,
        sender_id = user_id
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    
    return new_msg

async def get_recent_messages(room_id:UUID,db:AsyncSession, limit: int, offset: int):
    query = select(Message).options(selectinload(Message.sender)).where(Message.room_id == room_id).order_by(Message.posted_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    messages =  result.scalars().all()
    
    return messages

async def get_msgs_by_sender_name(room_id:UUID,name: str,db:AsyncSession, limit: int, offset: int):
    query = select(Message).join(User).where(Message.room_id == room_id,User.name.ilike(f"%{name}%")
).order_by(Message.posted_at.asc()).options(selectinload(Message.sender)).limit(limit).offset(offset)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return messages
async def get_msg_by_id(room_id: UUID, msg_id: UUID,db: AsyncSession):
    query = select(Message).where(Message.room_id == room_id,Message.id == msg_id)
    result = await db.execute(query)
    message = result.scalar_one_or_none()
    
    return message

async def update_message(msg_id: UUID,new_url: Optional[str],new_id: Optional[str],content:str,file: UploadFile,db:AsyncSession):
    updated_data = {
        "media_url" : new_url,
        "media_id"  : new_id,
        "content"   : content
    }
    stmt = update(Message).where(Message.id == msg_id).values(**updated_data).returning(Message)
    result = await db.execute(stmt)
    await db.commit()
    edited_message = result.scalar_one_or_none()
    
    return edited_message
    
    
async def delete_message(msg_id: UUID, room_id: UUID,db: AsyncSession):
    await db.execute(delete(Message).where(Message.room_id == room_id,Message.id == msg_id))
    
    await db.commit()
    

async def search_content(room_id:UUID,key_word: str,db:AsyncSession,limit: int, offset: int):
    query = select(Message).where(Message.room_id == room_id,Message.content.ilike(f"%{key_word}%")).options(selectinload(Message.sender)).order_by(Message.posted_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return messages


