from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.security import hash_password

async def get_user_by_email(db: AsyncSession, email:str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_id(db:AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession, user_data: dict):
    user_data["hashed_password"] = hash_password(user_data.pop("password"))

    stmt = insert(User).values(**user_data).returning(User)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()