from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.core.security import get_current_user, hash_password
from backend.app.models.user import User
from backend.app.schemas.user_schema import UpdateUserRequest, UserData, UserResponse

router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)


@router.get("", response_model=UserResponse)
async def get_current_user(
        user: User = Depends(get_current_user),
):
    return UserResponse(user=UserData.model_validate(user))


@router.patch("", response_model=dict)
async def update_user(
        update_data: UpdateUserRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    if update_data.fullname:
        user.fullname = update_data.fullname

    if update_data.email:
        existing = db.query(User).filter(User.email == update_data.email).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Email already taken")
        user.email = update_data.email

    if update_data.phone:
        user.phone = update_data.phone

    if update_data.password:
        user.password_hash = hash_password(update_data.password)

    db.commit()

    return {"message": "User updated successfully"}


@router.delete("", response_model=dict)
async def delete_user(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}