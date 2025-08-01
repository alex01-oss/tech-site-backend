import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status
from starlette.responses import FileResponse

from app.core.security import admin_required
from app.schemas.post_schema import ImageUploadResponse
from app.schemas.user_schema import UserData

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/images",
    tags=["Media"]
)


@router.get("/{filename}")
async def serve_image(filename: str):
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        logger.warning(f"Attempted path traversal attack with filename: {filename}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    file_path = os.path.join("app/static/images", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    logger.info(f"Serving image: {filename}")
    return FileResponse(file_path, media_type="image/png")


@router.post("/upload-image")
async def upload_image(
        file: UploadFile = File(...),
        user: UserData = Depends(admin_required)
):
    upload_dir = "app/static/images"

    if user.role != "admin":
        logger.warning(f"User {user.id} attempted to upload an image without admin privileges.")
        raise HTTPException(status_code=403, detail="You are not allowed to upload images")

    if file.content_type not in ["image/png", "image/jpeg", "image/webp"]:
        logger.warning(f"Attempted to upload file with unsupported content type: {file.content_type}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        logger.warning(f"Attempted to upload file with unsupported filename extension: {file.filename}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

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
