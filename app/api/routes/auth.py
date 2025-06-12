
from fastapi import APIRouter, Body, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.core.security import issue_tokens, verify_password, hash_password, decode_token, oauth2_scheme
from backend.app.models import User, RefreshToken
from backend.app.schemas.user_schema import LoginRequest, RegisterRequest, RefreshTokenRequest, LogoutRequest, \
    MessageResponse, TokenResponse, TokenBundle

router = APIRouter(
    prefix="/api/auth",
    tags=["Authorization"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
        user_data: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return TokenResponse(
        message="Login successful",
        **issue_tokens(user.id, db)
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed_password = hash_password(user.password)

        new_user = User(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()

        return TokenResponse(
            message="User registered successfully",
            **issue_tokens(new_user.id, db)
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User with this name already exists"
        )
        

@router.post("/refresh", response_model=TokenBundle)
async def refresh_token(
        refresh_data: RefreshTokenRequest = Body(...),
        db: Session = Depends(get_db),
):
    refresh_token = refresh_data.refresh_token

    payload = decode_token(refresh_token)
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if not user_id or token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_record = db.query(RefreshToken).filter_by(
        user_id=int(user_id),
        refresh_token=refresh_token
    ).first()

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or revoked token")

    db.delete(token_record)
    db.commit()

    return TokenBundle(
        **issue_tokens(int(user_id), db)
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    logout_data: LogoutRequest = Body(...),
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_token(access_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    refresh_token_entry = db.query(RefreshToken).filter_by(
        user_id=user_id,
        refresh_token=logout_data.refresh_token
    ).delete()
    db.commit()

    if not refresh_token_entry:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    return MessageResponse(
        message="Successfully logged out",
    )