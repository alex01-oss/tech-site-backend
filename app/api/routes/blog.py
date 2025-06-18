import datetime
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_db
from app.core.security import admin_required, get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post_schema import CreatePostRequest, DeletePostResponse, EditPostRequest, PostResponse
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserData
from app.utils.cache import cache_get, cache_set, redis_client

router = APIRouter(
    prefix="/api/blog",
    tags=["Blog"]
)


@router.post("", response_model=PostResponse)
async def create_post(
        data: CreatePostRequest,
        db: Session = Depends(get_db),
        user: UserData = Depends(admin_required)
):
    await redis_client.delete("posts_list")

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


@router.delete("/{post_id}", response_model=DeletePostResponse)
async def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    await redis_client.delete("posts_list")
    await redis_client.delete(f"post:{post_id}")

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


@router.put("/{post_id}")
async def update_post(
        post_id: int,
        data: EditPostRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    await redis_client.delete("posts_list")
    await redis_client.delete(f"post:{post_id}")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to edit this post")

    try:
        post.title = data.title
        post.content = data.content
        post.image = data.image
        post.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(post)
        return PostResponse.model_validate(post)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")


@router.get("", response_model=list[PostResponse])
async def get_all_posts(
        db: Session = Depends(get_db)
):
    try:
        cache_key = "posts_list"
        cached = await cache_get(cache_key)
        if cached:
            return [PostResponse(**p) for p in cached]

        posts = db.query(Post).order_by(Post.created_at.desc()).all()
        serialized = [PostResponse.model_validate(post).model_dump(mode="json") for post in posts]

        await cache_set(cache_key, serialized, ex=600)

        return [PostResponse(**p) for p in serialized]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
        post_id: int,
        db: Session = Depends(get_db)
):
    try:
        cache_key = f"post:{post_id}"
        cached = await cache_get(cache_key)
        if cached:
            return PostResponse(**cached)

        post = db.query(Post).filter(Post.id == post_id).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        serialized = PostResponse.model_validate(post).model_dump(mode="json")
        await cache_set(cache_key, serialized, ex=600)

        return PostResponse(**serialized)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch post: {str(e)}")
