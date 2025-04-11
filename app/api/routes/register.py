from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User
from app.schemas.user_schema import RegisterResponse, RegisterRequest

register_router = APIRouter()

@register_router.post("/api/register", response_model=RegisterResponse)
async def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):
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
    
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return {
      "message": "User registered successfully",
      "token": access_token,
      "refreshToken": refresh_token,
      "user": {
        "email": new_user.email,
        "username": new_user.username
      }
    }
