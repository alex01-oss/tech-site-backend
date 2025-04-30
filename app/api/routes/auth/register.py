from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User
from app.schemas.user_schema import RegisterResponse, RegisterRequest, UserData

register_router = APIRouter()

@register_router.post("/api/register", response_model=RegisterResponse)
async def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed_password = hash_password(user.password)

        new_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()

        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id, db)

        return RegisterResponse(
            message="User registered successfully",
            accessToken=access_token,
            refreshToken=refresh_token,
            user=UserData(
                id=new_user.id,
                role=new_user.role,
                email=new_user.email,
                username=new_user.username
            )
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User with this name already exists"
        )