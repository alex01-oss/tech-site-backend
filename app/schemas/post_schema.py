from pydantic import BaseModel, constr, Field
from datetime import datetime
from typing import Optional


class CreatePostRequest(BaseModel):
    title: constr(min_length=1) = Field(..., description="Post title")
    content: constr(min_length=1) = Field(..., description="Post content")
    image: str | None = None


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
