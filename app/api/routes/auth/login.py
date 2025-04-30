from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.schemas.user_schema import LoginResponse, LoginRequest, UserData

login_router = APIRouter()


@login_router.post("/api/login", response_model=LoginResponse)
async def login(
        user_data: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, db)

    user_data = UserData.model_validate(user)

    return LoginResponse(
        message="Login successful",
        user=user_data,
        accessToken=access_token,
        refreshToken=refresh_token,
    )