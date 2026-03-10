from fastapi import APIRouter, Depends, status,HTTPException,UploadFile,File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.db import get_db
from app.auth import create_user_token, get_current_user
from app.security import verify_password
from app.schemas.user import CreateUser
from app.crud.users import get_user_by_email, get_user_by_id, create_user
from app.imagekit import delete_from_imagekit, upload_to_imagekit
router = APIRouter(prefix="/auth",tags=["auth"])


@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def signup(data: CreateUser, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=data.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return await create_user(db, data.model_dump())

@router.post("/login",status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = await create_user_token(data={"user_id" : str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.patch("/profile/picture")
async def update_profile_pic(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.profile_pic_id:
        await delete_from_imagekit(current_user.profile_pic_id)
    
    new_url, new_id = await upload_to_imagekit(file)

    current_user.profile_pic_url = new_url
    current_user.profile_pic_id = new_id
    await db.commit()

    return {"url": new_url}

@router.delete("/profile/picture", status_code=status.HTTP_204_NO_CONTENT)
async def remove_profile_pic(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.profile_pic_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile picture to remove")
    
    await delete_from_imagekit(current_user.profile_pic_id)

    current_user.profile_pic_id = None
    current_user.profile_pic_url = None
    await db.commit()
