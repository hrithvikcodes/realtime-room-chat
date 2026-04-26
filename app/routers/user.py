from fastapi import APIRouter, Depends, status,HTTPException,UploadFile,File, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.refresh_token import RefreshToken
from datetime import datetime, timedelta
from app.db import get_db
from app.auth import (create_access_token, create_refresh_token, get_current_user,
    get_user_from_token, REFRESH_TOKEN_TIME)
from app.security import verify_password
from app.schemas.user import CreateUser, RefreshRequest
from app.crud.users import get_user_by_email, get_user_by_id, create_user
from app.imagekit import delete_from_imagekit, upload_to_imagekit
from app.logger import get_logger
from app.limiter import limiter
from fastapi.concurrency import run_in_threadpool
router = APIRouter(prefix="/auth",tags=["auth"])
logger = get_logger("user.router")

@router.post("/signup",status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def signup(data: CreateUser,request:Request, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=data.email)
    if db_user:
        logger.warning("Attempt to register with existing email")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    logger.info("New user registered", extra={"email": data.email})
    return await create_user(db, data.model_dump())

@router.post("/login",status_code=status.HTTP_200_OK)
@limiter.limit("100/minute")
async def login(request: Request,form_data: OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    user  : User | None =await get_user_by_email(db, form_data.username)
    password_valid = await run_in_threadpool(verify_password, form_data.password, user.hashed_password) if user else False
    if not user or not password_valid:
        logger.warning("Login attempt with invalid credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    assert user is not None

    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    access_token = await create_access_token(str(user.id)) 
    refresh_token = await create_refresh_token(str(user.id)) 

    db_token = RefreshToken(
        user_id = user.id,
        token = refresh_token,
        expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_TIME)
    )
    db.add(db_token)
    await db.commit()
    logger.info("User logged in", extra={"user_id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh",status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def refresh(request:Request,data: RefreshRequest,db: AsyncSession = Depends(get_db)):
    check_token = select(RefreshToken).where(RefreshToken.token == data.refresh_token)
    result = await db.execute(check_token)
    stored_token = result.scalar_one_or_none()
    if not stored_token :
        logger.warning("Refresh attempt with invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if stored_token.expires_at < datetime.now():
        await db.delete(stored_token)
        await db.commit()
        logger.warning("Refresh attempt with expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    
    try:
        user = await get_user_from_token(data.refresh_token, "refresh",db)
    except ValueError as e:
        logger.warning("Refresh token validation failed", extra={"error": str(e)})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    await db.delete(stored_token)
    
    new_refresh_token = await create_refresh_token(str(user.id))
    db.add(RefreshToken(
        user_id = user.id,
        token = new_refresh_token,
        expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_TIME)
    ))
    await db.commit()
    new_access_token = await create_access_token(str(user.id))
    logger.info("Token refreshed", extra={"user_id": user.id})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    
   

@router.post("/logout",status_code=status.HTTP_200_OK)  
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    check_token = select(RefreshToken).where(RefreshToken.token == data.refresh_token)
    result = await db.execute(check_token)
    stored_token = result.scalar_one_or_none()
    if stored_token:
        await db.delete(stored_token)
        await db.commit()
    logger.info("User logged out")
    return {"detail": "Logged out successfully"}
@router.patch("/profile/picture")
async def update_profile_pic(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.profile_pic_id:
        await delete_from_imagekit(current_user.profile_pic_id)
    
    new_url, new_id = await upload_to_imagekit(file)
    db.add(current_user)
    current_user.profile_pic_url = new_url
    current_user.profile_pic_id = new_id
    
    await db.commit()
    await db.refresh(current_user)
    logger.info("User updated profile picture", extra={"user_id": current_user.id})
    return {"profile_pic_url": new_url}

@router.delete("/profile/picture", status_code=status.HTTP_204_NO_CONTENT)
async def remove_profile_pic(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.profile_pic_id:
        logger.warning("Attempt to remove non-existent profile picture", extra={"user_id": current_user.id})    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile picture to remove")
    logger.info("User removed profile picture", extra={"user_id": current_user.id})
    await delete_from_imagekit(current_user.profile_pic_id)

    current_user.profile_pic_id = None
    current_user.profile_pic_url = None
    await db.commit()
