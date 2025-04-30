from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.post import Post
from app.schemas.post_schema import PostResponse

get_all_posts_router = APIRouter()


@get_all_posts_router.get("/api/blog", response_model=list[PostResponse])
async def get_all_posts(
        db: Session = Depends(get_db)
):
    try:
        posts = db.query(Post).order_by(Post.created_at.desc()).all()
        return [PostResponse.model_validate(post) for post in posts]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")
