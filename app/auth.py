import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from app.db import async_session_maker, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM") or ""
ACCESS_TOKEN_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def create_user_token(data: dict):
    payload = data.copy()

    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_TIME)
    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_token(token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("Invalid token: No user_id")
    except JWTError:
        raise ValueError("Couldnot validate credentials")
    
    async with async_session_maker() as db:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not Found")
    return user
'''
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        user_id =  payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
'''
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return await get_user_from_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed"
        )