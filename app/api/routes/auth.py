from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Cookie
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.security import issue_tokens, verify_password, hash_password, decode_token, get_current_user
from app.core.settings import settings
from app.models import User, RefreshToken
from app.schemas.user_schema import LoginRequest, RegisterRequest, RefreshTokenRequest, LogoutRequest, \
    MessageResponse, TokenResponse, TokenBundle


def set_auth_cookies(response: Response, tokens: dict):
    response.set_cookie(
        key="access_token",
        value=f"Bearer {tokens['access_token']}",
        httponly=True,
        secure=settings.HTTPS_ENABLED,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {tokens['refresh_token']}",
        httponly=True,
        secure=settings.HTTPS_ENABLED,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

def delete_auth_cookies(response: Response):
    response.delete_cookie(
        key="access_token",
        secure=settings.HTTPS_ENABLED,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        secure=settings.HTTPS_ENABLED,
        httponly=True,
        samesite="lax",
    )

router = APIRouter(
    prefix="/api/auth",
    tags=["Authorization"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
        user_data: LoginRequest,
        response: Response,
        db: Session = Depends(get_db),
):
    # noinspection PyTypeChecker
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    tokens = issue_tokens(user.id, db)

    set_auth_cookies(response, tokens)

    return TokenResponse(
        message="Login successful",
        **tokens
    )


@router.post("/register", response_model=TokenResponse)
async def register(
        user_data: RegisterRequest,
        response: Response,
        db: Session = Depends(get_db)
):
    try:
        # noinspection PyTypeChecker
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = hash_password(user_data.password)

        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        tokens = issue_tokens(new_user.id, db)

        set_auth_cookies(response, tokens)

        return TokenResponse(
            message="User registered successfully",
            **tokens
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or phone number might already exist."
        )


@router.post("/refresh", response_model=TokenBundle)
async def refresh_token_route(
        response: Response,
        db: Session = Depends(get_db),
        refresh_data: Optional[RefreshTokenRequest] = Body(None),
        refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")
):
    token_str = None
    if refresh_data and refresh_data.refresh_token:
        token_str = refresh_data.refresh_token
    elif refresh_token_cookie:
        token_str = refresh_token_cookie

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing from body or cookie"
        )

    if token_str.startswith("Bearer "):
        token_str = token_str[7:]

    try:
        payload = decode_token(token_str)
    except HTTPException as e:
        raise e

    user_id = payload.get("sub")
    token_type = payload.get("type")

    if not user_id or token_type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_record = db.query(RefreshToken).filter_by(
        user_id=int(user_id),
        refresh_token=token_str
    ).first()

    if not token_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked token")

    db.delete(token_record)
    db.commit()

    new_tokens = issue_tokens(int(user_id), db)

    set_auth_cookies(response, new_tokens)

    return TokenBundle(
        **new_tokens
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
        response: Response,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        logout_data: Optional[LogoutRequest] = Body(None),
        refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")
):
    user_id = current_user.id

    refresh_token_to_revoke = None
    if logout_data and logout_data.refresh_token:
        refresh_token_to_revoke = logout_data.refresh_token
    elif refresh_token_cookie:
        refresh_token_to_revoke = refresh_token_cookie

    if not refresh_token_to_revoke:
        delete_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing from body or cookie"
        )

    try:
        payload = decode_token(refresh_token_to_revoke)
        token_user_id = payload.get("sub")
        token_type = payload.get("type")

        if not token_user_id or token_type != "refresh" or int(token_user_id) != user_id:
            delete_auth_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Provided refresh token is invalid or does not belong to user"
            )
    except HTTPException as e:
        delete_auth_cookies(response)
        raise e

    refresh_token_entry = db.query(RefreshToken).filter_by(
        user_id=user_id,
        refresh_token=refresh_token_to_revoke
    ).delete()
    db.commit()

    if not refresh_token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")

    delete_auth_cookies(response)

    return MessageResponse(
        message="Successfully logged out",
    )