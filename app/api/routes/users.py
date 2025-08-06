import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user, hash_password
from app.models.user import User
from app.schemas.user_schema import UpdateUserRequest, UserData, MessageResponse, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)


@router.get("", response_model=UserResponse)
async def get_user(
        user: User = Depends(get_current_user),
):
    logger.info(f"User profile requested for user_id: {user.id}")
    return UserResponse(user=UserData.model_validate(user))


@router.patch("", response_model=MessageResponse)
async def update_user(
        update_data: UpdateUserRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    logger.info(f"Attempting to update user_id: {user.id} with data: {update_data.model_dump(exclude_unset=True)}")

    if update_data.full_name:
        user.full_name = update_data.full_name

    if update_data.email:
        # noinspection PyTypeChecker
        existing = db.query(User).filter(User.email == update_data.email).first()
        if existing and existing.id != user.id:
            logger.warning(
                f"Update failed for user {user.id}: email '{update_data.email}' already taken by user {existing.id}.")
            raise HTTPException(status_code=409, detail="Email already taken")
        user.email = update_data.email

    if update_data.phone:
        user.phone = update_data.phone

    if update_data.password:
        user.password_hash = hash_password(update_data.password)

    db.commit()

    logger.info(f"User {user.id} updated successfully.")
    return MessageResponse(message="User updated successfully")


@router.delete("", response_model=dict)
async def delete_user(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    logger.warning(f"Attempting to delete user_id: {user.id}")

    db.delete(user)
    db.commit()

    logger.info(f"User {user.id} deleted successfully.")
    return MessageResponse(message="User deleted successfully")
