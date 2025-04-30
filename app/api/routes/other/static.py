import os

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

static_router = APIRouter()

@static_router.get("/images/{filename}")
async def serve_image(filename: str):
    file_path = os.path.join("app/static/images", filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    raise HTTPException(status_code=404, detail="File not found")