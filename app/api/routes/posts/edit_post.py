import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post_schema import EditPostRequest, PostResponse

edit_post_router = APIRouter()


@edit_post_router.put("/api/blog/{post_id}")
async def update_post(
        post_id: int,
        data: EditPostRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to edit this post")

    try:
        post.title = data.title
        post.content = data.content
        post.image = data.image
        post.updated_at = datetime.datetime.now(),

        db.commit()
        db.refresh(post)
        return PostResponse.model_validate(post)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")