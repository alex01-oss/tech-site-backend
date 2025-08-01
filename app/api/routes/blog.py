import datetime
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.security import admin_required, get_current_user
from app.models.post import Post
from app.models.user import User
from app.schemas.post_schema import CreatePostRequest, DeletePostResponse, EditPostRequest, PostResponse
from app.schemas.user_schema import UserData
from app.utils.cache import cache_get, cache_set, redis_client
from app.utils.sanitize_html import sanitize_html

logger = logging.getLogger(__name__)

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

    new_post = Post(
        user_id=user.id,
        image=data.image,
        title=sanitize_html(data.title),
        content=sanitize_html(data.content),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    logger.info(f"New post created by user {user.id} with ID {new_post.id}")
    return PostResponse.model_validate(new_post)


@router.delete("/{post_id}", response_model=DeletePostResponse)
async def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    await redis_client.delete("posts_list")
    await redis_client.delete(f"post:{post_id}")

    post = db.query(Post).filter(and_(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this post")

    db.delete(post)
    db.commit()

    logger.info(f"Post {post_id} deleted by user {user.id}")
    return DeletePostResponse(detail="Post deleted successfully")


@router.put("/{post_id}")
async def update_post(
        post_id: int,
        data: EditPostRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    await redis_client.delete("posts_list")
    await redis_client.delete(f"post:{post_id}")

    post = db.query(Post).filter(and_(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to edit this post")

    post.title = sanitize_html(data.title)
    post.content = sanitize_html(data.content)
    post.image = data.image
    post.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(post)

    logger.info(f"Post {post_id} updated by user {user.id}")
    return PostResponse.model_validate(post)


@router.get("", response_model=list[PostResponse])
async def get_all_posts(
        db: Session = Depends(get_db),
        limit: Optional[int] = None
):
    cache_key = f"posts_list_limit_{limit if limit is not None else 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return [PostResponse(**p) for p in cached]

    query = db.query(Post).order_by(Post.created_at.desc())

    if limit is not None:
        query = query.limit(limit)

    posts = query.all()

    serialized = [PostResponse.model_validate(post).model_dump(mode="json") for post in posts]

    await cache_set(cache_key, serialized, ex=600)

    return [PostResponse(**p) for p in serialized]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
        post_id: int,
        db: Session = Depends(get_db)
):
    cache_key = f"post:{post_id}"
    cached = await cache_get(cache_key)
    if cached:
        return PostResponse(**cached)

    post = db.query(Post).filter(and_(Post.id == post_id)).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    serialized = PostResponse.model_validate(post).model_dump(mode="json")
    await cache_set(cache_key, serialized, ex=600)

    return PostResponse(**serialized)
