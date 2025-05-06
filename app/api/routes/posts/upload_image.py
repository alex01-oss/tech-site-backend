import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.core.security import admin_required
from app.schemas.post_schema import ImageUploadResponse
from app.schemas.user_schema import UserData

upload_image_router = APIRouter()


@upload_image_router.post("/api/upload-image")
async def upload_image(
        file: UploadFile = File(...),
        user: UserData = Depends(admin_required)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to upload images")

    upload_dir = "app/static/images"

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    file_url = f"images/{filename}"

    return ImageUploadResponse(
        filename=filename,
        url=file_url
    )
