from fastapi import APIRouter, Body, Depends, HTTPException
from psycopg2 import IntegrityError

from app.schemas.user_schema import LoginRequest, LoginResponse, LogoutRequest, LogoutResponse, RefreshTokenRequest, RefreshTokenResponse, RegisterRequest, RegisterResponse, UserData
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password, oauth2_scheme
from app.models.refresh_token import RefreshToken
from app.api.dependencies import get_db
from sqlalchemy.orm import Session
from app.models.user import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authorization"]
)


@router.post("/login", response_model=LoginResponse)
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
        access_token=access_token,
        refresh_token=refresh_token,
    )
    

@router.post("/register", response_model=RegisterResponse)
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

        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id, db)

        return RegisterResponse(
            message="User registered successfully",
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserData(
                id=new_user.id,
                full_name=new_user.full_name,
                email=new_user.email,
                phone=new_user.phone,
                role=new_user.role,
            )
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User with this name already exists"
        )
        

@router.post("/refresh", response_model=RefreshTokenResponse)
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

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id, db)

    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=LogoutResponse)
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

    return LogoutResponse(
        message="Successfully logged out",
    )