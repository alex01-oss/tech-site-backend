import logging
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Cookie, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.security import issue_tokens, verify_password, hash_password, decode_token, get_current_user, \
    set_auth_cookies, delete_auth_cookies
from app.models import User, RefreshToken
from app.schemas.user_schema import LoginRequest, RegisterRequest, RefreshTokenRequest, LogoutRequest, \
    MessageResponse, TokenResponse, TokenBundle

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authorization"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
        user_data: LoginRequest,
        response: Response,
        request: Request,
        db: Session = Depends(get_db),
):
    # noinspection PyTypeChecker
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    tokens = issue_tokens(user.id, db, request)
    set_auth_cookies(response, tokens)

    logger.info(f"Successful login for user_id: {user.id}")
    return TokenResponse(
        message="Login successful",
        **tokens
    )


@router.post("/register", response_model=TokenResponse)
async def register(
        user_data: RegisterRequest,
        response: Response,
        request: Request,
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

        tokens = issue_tokens(new_user.id, db, request)
        set_auth_cookies(response, tokens)

        return TokenResponse(
            message="User registered successfully",
            **tokens
        )

    except IntegrityError:
        db.rollback()
        logger.error(f"IntegrityError during registration for email: {user_data.email}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or phone number might already exist."
        )


@router.post("/refresh", response_model=TokenBundle)
async def refresh_token_route(
        response: Response,
        request: Request,
        db: Session = Depends(get_db),
        refresh_data: Optional[RefreshTokenRequest] = Body(None),
        refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")
):
    token_str = refresh_data.refresh_token if refresh_data and refresh_data.refresh_token else refresh_token_cookie

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing from body or cookie"
        )

    if token_str.startswith("Bearer "):
        token_str = token_str[7:]

    payload = decode_token(token_str)

    user_id = payload.get("sub")
    token_type = payload.get("type")
    jti = payload.get("jti")

    if not user_id or token_type != "refresh" or not jti:
        delete_auth_cookies(response)
        logger.warning("Invalid refresh token payload during refresh request.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_record = db.query(RefreshToken).filter_by(
        user_id=int(user_id),
        jti=jti,
        is_revoked=False
    ).first()

    if not token_record or token_record.refresh_token != token_str:
        if token_record and token_record.is_revoked:
            logger.warning(
                f"Revoked token (JTI: {jti}) attempted by user {user_id}. All user tokens may be compromised.")
        delete_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked token")

    db.delete(token_record)
    db.commit()

    new_tokens = issue_tokens(int(user_id), db, request)
    set_auth_cookies(response, new_tokens)

    logger.info(f"Refresh token successful for user_id: {user_id}. New tokens issued.")
    return TokenBundle(**new_tokens)


@router.post("/logout", response_model=MessageResponse)
async def logout(
        response: Response,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        logout_data: Optional[LogoutRequest] = Body(None),
        refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")
):
    user_id = current_user.id

    refresh_token_to_revoke = logout_data.refresh_token if logout_data and logout_data.refresh_token else refresh_token_cookie

    if not refresh_token_to_revoke:
        delete_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing from body or cookie"
        )

    try:
        payload = decode_token(refresh_token_to_revoke)
    except HTTPException as e:
        print(f"DEBUG: Logout failed due to token error, but clearing cookies: {e.detail}")
        delete_auth_cookies(response)
        raise e

    token_user_id = payload.get("sub")
    jti = payload.get("jti")
    token_type = payload.get("type")

    if not token_user_id or token_type != "refresh" or not jti or int(token_user_id) != user_id:
        delete_auth_cookies(response)
        logger.warning(f"Logout attempt with a token that does not belong to user {user_id}. Cleared cookies.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided refresh token is invalid or does not belong to user"
        )

    token_record = db.query(RefreshToken).filter_by(
        user_id=user_id,
        jti=jti,
    ).first()

    if token_record:
        db.delete(token_record)
        db.commit()
        logger.info(f"Refresh token with JTI {jti} successfully revoked for user {user_id}.")
    else:
        logger.warning(
            f"Refresh token with JTI {jti} not found for user {user_id} during logout. It might have already expired or been revoked.")

    delete_auth_cookies(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout-all", response_model=MessageResponse)
async def logout_other_devices(
        response: Response,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # noinspection PyTypeChecker
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.commit()
    delete_auth_cookies(response)
    logger.info(f"All refresh tokens for user {user.id} have been revoked.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/forgot-password", response_model=str)
async def forgot_password():
    pass