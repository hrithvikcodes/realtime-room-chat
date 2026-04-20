from app.imagekit import upload_to_imagekit
import secrets
from sqlalchemy import delete, insert,update, select, desc
from app.models.room import Role, RoomMember
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi  import Form, UploadFile, File
from app.schemas.room import RoomCreate
from app.models.room import Room
from uuid import UUID
from sqlalchemy.orm import joinedload, selectinload


async def create_db_room(db:AsyncSession,room_data: RoomCreate, user_id : UUID):
    db_room = Room(
        **room_data.model_dump(),
        created_by = user_id,    
    )
    db.add(db_room)
    await db.flush()
    member = RoomMember(
        user_id = user_id,
        room_id = db_room.id,
        role = Role.ADMIN
    )
    db.add(member)

    await db.commit()
    return db_room
async def update_room_details(db:AsyncSession,room_id: UUID,room_data: RoomCreate):
    stmt = update(Room).where(Room.id == room_id).values(**room_data.model_dump()).returning(Room)
    result = await db.execute(stmt)
    await db.commit()
    updated_data = result.scalar_one_or_none()
    return updated_data

async def join_db_room(db:AsyncSession,user_id : UUID,room_id: UUID):
    new_member = RoomMember(
        user_id = user_id,
        room_id = room_id,
        role = Role.MEMBER
    )
    db.add(new_member)
    await db.commit()
    return {"msg": "Joined Room Successfully"}

async def get_room_by_invite_code(db:AsyncSession, invite_code:str):
    room_query = select(Room).where(Room.invite_code == invite_code)
    result = await db.execute(room_query)
    room = result.scalar_one_or_none()
    return room

async def regenerate_invite_code(db:AsyncSession, room_id: UUID):
    print(f"Looking for room_id: {room_id}, type: {type(room_id)}")
    
    room = await get_room_by_id(db, room_id)
    print(f"Found room: {room}")
    if room:
        room.invite_code = secrets.token_urlsafe(16)
        await db.commit()
        await db.refresh(room)
    return room
    

async def get_room_by_id(db:AsyncSession, room_id:UUID):
    room_query = select(Room).where(Room.id == room_id)
    result = await db.execute(room_query)
    room = result.scalar_one_or_none()
    return room
async def list_rooms_in_db(db:AsyncSession):
    query = select(Room).order_by(desc(Room.created_at))
    result = await db.execute(query)
    rooms = result.scalars().all()
    return rooms
async def search_for_rooms(room_name:str,db: AsyncSession,limit: int,offset: int):
    query = select(Room).where(Room.name.ilike(f"%{room_name}%")).limit(limit).offset(offset)
    result = await db.execute(query)
    rooms = result.scalars().all()
    return rooms
async def get_db_room_members(db:AsyncSession,room_id: UUID):
    query = select(RoomMember).where(RoomMember.room_id == room_id).options(selectinload(RoomMember.user))
    result = await db.execute(query)
    members = result.scalars().all()
    return members

async def get_my_db_rooms(db:AsyncSession, user_id: UUID):
    query = select(Room).join(RoomMember).where(RoomMember.user_id == user_id)
    result = await db.execute(query)
    members = result.scalars().all()
    return members

async def leave_db_room(db:AsyncSession, membership: RoomMember):
    await db.delete(membership)
    await db.commit()

async def get_membership(db: AsyncSession, room_id: UUID, user_id: UUID):
    """"""
    stmt = select(RoomMember).where(
        RoomMember.room_id == room_id, 
        RoomMember.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def remove_room_member(db: AsyncSession, membership : RoomMember):
    await db.delete(membership)
    await db.commit()

async def delete_db_room(db:AsyncSession, membership : RoomMember):
    room_query = select(Room).where(Room.id == membership.room_id)
    result = await db.execute(room_query)
    room = result.scalar_one_or_none()
    if room:
        await db.execute(delete(RoomMember).where(RoomMember.room_id == membership.room_id))
        await db.delete(room)
        await db.commit()



    

