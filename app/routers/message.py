

from fastapi import Depends, APIRouter, File, UploadFile, status, HTTPException, Form, Query
from app.imagekit import delete_from_imagekit, imagekit, upload_to_imagekit
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user
from app.db import get_db
from app.models.user import User
from uuid import UUID
from fastapi.concurrency import run_in_threadpool
from app.websocket_manager import manager
from app.chat_cache import cache_message, get_cached_messages
from app.crud.messages import (delete_message, get_msg_by_id, get_msgs_by_sender_name,
    get_recent_messages,  search_content, send_message, update_message)
from app.crud.rooms import get_membership
from app.schemas.message import MessageResponse
from app.logger import get_logger
logger = get_logger("message.router")


router = APIRouter(prefix="/messages",tags=["messages"])

@router.post("/{room_id}/send",status_code=status.HTTP_201_CREATED)
async def send_messages(room_id:UUID,content:str= Form(...),file:UploadFile=File(None),db:AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized message send attempt", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")
    
    message = await send_message(room_id,current_user.id,db,content,file)
    if not message:
        logger.warning("Message not found", extra={"room_id": room_id, "user_id": current_user.id})

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Message not found")
    message_data = {
        "sender": current_user.name,
        "content": content,
        "created_at": str(message.posted_at),
        "media_url": message.media_url
    }
    try:
        await manager.broadcast_to_room(room_id, message_data)
        
    except Exception as e:
        logger.error("Failed to broadcast message to WebSocket clients", extra={"room_id": room_id, "error": str(e)})
    try:
        await cache_message(room_id, message_data)
    except Exception as e:   
        logger.error("Failed to cache message", extra={"room_id": room_id, "error": str(e)})
    return message

@router.get("/{room_id}/recent",status_code=status.HTTP_200_OK)
async def recent_messages(room_id: UUID,db: AsyncSession = Depends(get_db),current_user: User= Depends(get_current_user),limit: int = Query(20, ge=1, le=100),offset: int = Query(0, ge= 0)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized recent messages access attempt", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    cached = await get_cached_messages(room_id)
    if cached:
        return cached
    messages = await get_recent_messages(room_id,db,limit,offset)
    if not messages:
        logger.info("No recent messages found", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Messages not found")
    return messages

@router.get("/{room_id}",response_model=list[MessageResponse],status_code=status.HTTP_200_OK)
async def get_messages_by_sender_name(room_id:UUID,name: str,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user), limit: int = Query(0,ge=1,le=100),offset: int = Query(0, ge=0)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized message search attempt", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    messages = await get_msgs_by_sender_name(room_id,name,db,limit,offset)
    if messages is None:
        return []
    return messages
@router.get("/{room_id}/{key_word}",status_code=status.HTTP_200_OK,response_model=list[MessageResponse])
async def search_in_messages(room_id: UUID, key_word: str,db:AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user), limit: int = Query(0, ge=1,le=100),offset: int = Query(0, ge=0)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized message search attempt", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    messages = await search_content(room_id,key_word,db,limit,offset)
    if not messages:
        logger.info("No messages found matching the search criteria", extra={"room_id": room_id, "keyword": key_word})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Message not found")
    return messages
    
@router.put("/edit/{room_id}/{msg_id}",status_code=status.HTTP_200_OK)
async def edit_message(msg_id: UUID,room_id:UUID,file:UploadFile = File(...),content: str =Form(...),db:AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized message edit attempt", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    message = await get_msg_by_id(room_id,msg_id,db)
    if not message:
        logger.warning("Message not found", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if message and message.media_id:
        try:
            await run_in_threadpool(imagekit.files.delete,message.media_id)
        except Exception as e:
            logger.error("Failed to delete old media from ImageKit", extra={"message_id": msg_id, "error": str(e)})
    new_url, new_id = await upload_to_imagekit(file)

    await update_message(msg_id,new_url,new_id,content,file,db)
    return update_message

@router.delete("/delete/{room_id}/{msg_id}",status_code=status.HTTP_204_NO_CONTENT)
async def unsend_message(room_id: UUID, msg_id: UUID,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized message delete attempt", extra={"room_id": room_id, "user_id": current_user.id})   
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    message = await get_msg_by_id(room_id,msg_id,db)
    if not message:
        logger.warning("Message not found for deletion", extra={"room_id": room_id, "message_id": msg_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Message not found")
    if message and message.media_id:
        try:
            await imagekit.files.delete(message.media_id)
            logger.info("Old media deleted from ImageKit", extra={"message_id": msg_id})
        except Exception as e:
            logger.error("Failed to delete old media from ImageKit", extra={"message_id": msg_id, "error": str(e)})

    return await delete_message(msg_id,room_id,db)