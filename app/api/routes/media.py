import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.responses import FileResponse

from backend.app.core.security import admin_required
from backend.app.schemas.post_schema import ImageUploadResponse
from backend.app.schemas.user_schema import UserData

router = APIRouter(
    prefix="/api/images",
    tags=["Media"]
)


@router.get("/{filename}")
async def serve_image(filename: str):
    file_path = os.path.join("app/static/images", filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    raise HTTPException(status_code=404, detail="File not found")


@router.post("/upload-image")
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
