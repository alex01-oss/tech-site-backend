import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.security import get_current_user, hash_data, hash_for_check
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user_schema import UpdateUserRequest, UserData, MessageResponse, UserResponse

from app.core.encryption import encryption_service

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
    safe_data = update_data.model_dump(exclude_unset=True, exclude={'password'})
    logger.info(f"Attempting to update user_id: {user.id} with data: {safe_data}")

    if update_data.full_name:
        user.full_name = update_data.full_name

    if update_data.email:
        encrypted_email = encryption_service.encrypt_data(update_data.email)
        hashed_email = hash_for_check(update_data.email)
                    
        existing = db.query(User).filter(
            User.email_hash == hashed_email,
            User.id != user.id
        ).first()
        
        if existing:
            logger.warning(f"Update failed for user {user.id}: email already taken")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already taken"
            )
        user.email = encrypted_email
        user.email_hash = hashed_email

    if update_data.phone:
        encrypted_phone = encryption_service.encrypt_data(update_data.phone)
        hashed_phone = hash_for_check(update_data.phone)

        existing = db.query(User).filter(
            User.phone_hash == hashed_phone,
            User.id != user.id
        ).first()
        if existing:
            logger.warning(f"Update failed for user {user.id}: phone already taken")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Phone already taken"
            )
        user.phone = encrypted_phone
        user.phone_hash = hashed_phone

    if update_data.password:
        user.password_hash = hash_data(update_data.password)

    db.commit()

    logger.info(f"User {user.id} updated successfully.")
    return MessageResponse(message="User updated successfully")


@router.delete("", response_model=MessageResponse)
async def delete_user(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    logger.warning(f"Attempting to delete user_id: {user.id}")

    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()

    db.delete(user)
    db.commit()

    logger.info(f"User {user.id} deleted successfully.")
    return MessageResponse(message="User deleted successfully")
