from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreatePostRequest(BaseModel):
    title: str
    content: str
    image: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class EditPostRequest(BaseModel):
    title: str
    content: str
    image: Optional[str] = None


class DeletePostResponse(BaseModel):
    detail: str

class ImageUploadResponse(BaseModel):
    filename: str
    url: str