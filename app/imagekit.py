
from imagekitio import AsyncImageKit
import os
from fastapi import HTTPException, status, UploadFile



imagekit = AsyncImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)

async def upload_to_imagekit(file: UploadFile):
    MAX_SIZE = 25*1024*1024
    if file.size and file.size >MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File  too large")
    
    file_bytes = await file.read()
    if len(file_bytes)> MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail= "File  too large")
    result = await imagekit.files.upload(
        file=file_bytes,
        file_name= str(file.filename),
        use_unique_file_name=True,
    )
    return result.url , result.file_id

async def delete_from_imagekit(file_id: str):
    if file_id:
        
        await imagekit.files.delete(file_id)


