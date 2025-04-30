
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post_schema import DeletePostResponse

delete_post_router = APIRouter()


@delete_post_router.delete("/api/blog/{post_id}", response_model=DeletePostResponse)
async def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this post")

    try:
        db.delete(post)
        db.commit()
        return DeletePostResponse(detail="Post deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")
