import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import  OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from app.db import async_session_maker, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from uuid import UUID
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM") or ""
ACCESS_TOKEN_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
REFRESH_TOKEN_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS",7))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def create_access_token(user_id: str):
    payload = {
      "user_id": user_id,
      "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_TIME),
      "type": "access"
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
async def create_refresh_token(user_id: str):
    payload = {
      "user_id": user_id,
      "exp": datetime.now() + timedelta(days=REFRESH_TOKEN_TIME),
      "type": "refresh"
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

async def get_user_from_token(token: str, expected_type : str, db: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        print("PAYLOAD:", payload)

        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type")
        user_id = UUID(payload.get("user_id"))
        print("USER ID:", user_id)
        if user_id is None:
            raise ValueError("Invalid token: No user_id")
    except JWTError:
        raise ValueError("Couldnot validate credentials")
    
    async with async_session_maker() as db:
        user_id = UUID(payload.get("user_id"))
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not Found")
    return user

async def get_current_user(token: str = Depends(oauth2_scheme),db:AsyncSession = Depends(get_db)):
    try:
        return await get_user_from_token(token, "access",db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed"
        )
