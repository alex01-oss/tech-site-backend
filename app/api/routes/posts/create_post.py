import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import admin_required
from app.models.post import Post
from app.schemas.post_schema import CreatePostRequest, PostResponse
from app.schemas.user_schema import UserData

create_post_router = APIRouter()


@create_post_router.post("/api/blog", response_model=PostResponse)
async def create_post(
        data: CreatePostRequest,
        db: Session = Depends(get_db),
        user: UserData = Depends(admin_required)
):
    try:
        new_post = Post(
            user_id=user.id,
            image=data.image,
            title=data.title,
            content=data.content,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return PostResponse.model_validate(new_post)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")
