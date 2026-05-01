
from fastapi import Depends, APIRouter, File, UploadFile, status, HTTPException, Query, Request
from app.imagekit import upload_to_imagekit, delete_from_imagekit
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user
from app.db import get_db
from app.schemas.room import RoomCreate, RoomMemberResponse, RoomResponse
from app.models.user import User
from app.models.room import  Role
from app.models.message import Message

from app.crud.rooms import (create_db_room, delete_db_room, get_db_room_members, get_membership,
    get_my_db_rooms, get_room_by_id, get_room_by_invite_code, join_db_room, leave_db_room, 
    regenerate_invite_code, remove_room_member, update_room_details)
from uuid import UUID
from app.ai_service import summarize_chat_history
from app.chat_cache import format_messages_for_ai
from app.logger import get_logger
from app.limiter import limiter, get_user_or_ip
router = APIRouter(prefix="/room",tags=["room"])
logger = get_logger("room.router")

    

@router.post("/create_room",response_model=RoomResponse,status_code=status.HTTP_201_CREATED)
async def create_room(room:RoomCreate,db:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_db_room(db=db,room_data=room,user_id = current_user.id)
@router.put("/{room_id}/update-details",status_code=status.HTTP_200_OK,response_model=RoomResponse)
async def update_room_data(room_id: UUID,data: RoomCreate,db:AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Unauthorized room update attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin room update attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can update room details")
    updated_room =  await update_room_details(db,room_id,data)
    if not updated_room:
        logger.error("Room not found for update", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Room not found")
    return updated_room
@router.post("/{room_id}/join",status_code=status.HTTP_200_OK)
@limiter.limit("100/minute")
async def join_room(request:Request,room_id: UUID,invite_code: str = Query(...),db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    room = await get_room_by_id(db,room_id)
    if not room:
        logger.warning("Attempt to join non-existent room", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Room doesn't exist")
    if room.invite_code != invite_code:
        logger.warning("Invalid invite code used", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid invite code")
    
    membership = await get_membership(db, room_id, current_user.id)
    if membership:
        logger.warning("User already a member", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Already a member")
    return await join_db_room(db, current_user.id, room_id)
@router.get("/{room_id}/invite",status_code=status.HTTP_200_OK)
async def get_invite_code(room_id: UUID,db:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = await get_room_by_id(db,room_id)
    if not room:
        logger.warning("Attempt to access invite code for non-existent room", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Room not found ")
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Authentication failed", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    return {
        "invite_code": room.invite_code
    }
@router.put("/{room_id}/invite/regenerate",status_code=status.HTTP_201_CREATED)
async def regenerate_invite(room_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = await get_room_by_id(db,room_id)
    if not room:
        logger.warning("Attempt to regenerate invite code for non-existent room", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Room not found ")
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Authentication failed for invite code regeneration", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin attempt to regenerate invite code", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can regenerate invite code.")
    room_invite_code = await regenerate_invite_code(db, room_id)
    return {
        "invite_code": room_invite_code.invite_code  # type: ignore
    }
                                
@router.get("/my-rooms",response_model=list[RoomResponse],status_code=status.HTTP_200_OK)
async def my_rooms(db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    return await get_my_db_rooms(db,current_user.id)

@router.get("/{room_id}/members",response_model=list[RoomMemberResponse],status_code=status.HTTP_200_OK)
async def room_members(room_id:UUID,db:AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to access room members", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication Failed")
    return await get_db_room_members(db,room_id)


@router.delete("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(room_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to leave room", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")
    await leave_db_room(db,membership)

@router.delete("/{room_id}/remove/{target_user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def kick_member(room_id: UUID, target_user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to kick member", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin attempt to kick member", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins have permission to kick members")
    target_membership = await get_membership(db,room_id, target_user_id)
    if not target_membership:
        logger.warning("Target member not found", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target Member not found")
    if target_membership.role == Role.ADMIN:
        logger.warning("Attempt to kick another admin", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=400, detail="Cannot kick another administrator")
    
    await remove_room_member(db, target_membership)

@router.delete("/{room_id}/delete",status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to delete room", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not a member")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin attempt to delete room", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can delete a room")
    
    await delete_db_room(db, membership)



@router.patch("/{room_id}/profile/picture",status_code=status.HTTP_201_CREATED)
async def update_profile_picture(
    room_id: UUID,
    file: UploadFile = File(...),
    current_user : User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)

):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to update room profile picture", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication Failed")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin attempt to update room profile picture", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Only Admin can update room profile picture")
    
    room = await get_room_by_id(db, room_id)
    if not room:
        logger.warning("Attempt to update profile picture for non-existent room", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.profile_id:
        logger.info("Existing profile picture found, deleting...", extra={"room_id": room_id, "profile_id": room.profile_id})
        await delete_from_imagekit(room.profile_id)
    
    url, file_id = await upload_to_imagekit(file)
    room.profile_id = file_id
    room.profile_url = url

    await db.commit()

    logger.info("Room profile picture updated", extra={"room_id": room_id, "profile_id": file_id})
    return {"profile_url": url}

@router.delete("/{room_id}/profile/picture",status_code=status.HTTP_204_NO_CONTENT)
async def remove_profile_picture(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = await get_membership(db,room_id,current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to remove room profile picture", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not a Member")
    if membership.role != Role.ADMIN:
        logger.warning("Non-admin attempt to remove room profile picture", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Authentication failed")
    
    room = await get_room_by_id(db,room_id)
    if not room:
        logger.warning("Attempt to remove profile picture for non-existent room", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if not room.profile_id:
        logger.warning("Attempt to remove non-existent profile picture", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room has no profile picture to remove")
    
    await delete_from_imagekit(room.profile_id)
    room.profile_id = None
    room.profile_url = None
    await db.commit()

@router.get("/{room_id}/summary", status_code=status.HTTP_200_OK)
@limiter.limit("5/hour",key_func=get_user_or_ip) # type: ignore
async def get_chat_summary(request:Request,room_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = await get_membership(db, room_id, current_user.id)
    if not membership:
        logger.warning("Unauthorized attempt to access chat summary", extra={"room_id": room_id, "user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")

    formatted_messages = await format_messages_for_ai(room_id)

    if not formatted_messages:
        logger.warning("No messages found for chat summary", extra={"room_id": room_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No conversation found")

    ai_summary = await summarize_chat_history(formatted_messages)
    logger.info("Generated chat summary", extra={"room_id": room_id, "summary_length": len(ai_summary)})
    return {"summary": ai_summary}






