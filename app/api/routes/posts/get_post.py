from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.post import Post
from app.schemas.post_schema import PostResponse

get_post_router = APIRouter()


@get_post_router.get("/api/blog/{post_id}", response_model=PostResponse)
async def get_post_by_id(
        post_id: int,
        db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)
