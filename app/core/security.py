from datetime import timedelta, datetime
from typing import Union, Any, Type, Optional

import jwt
from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.settings import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def hash_password(password) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(identity: Union[str, Any]) -> str:
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(identity), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(identity: Union[str, Any]) -> str:
    expire = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(identity), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Type[User]:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user=db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# OPTIONAL
def oauth2_scheme_optional(authorization: str = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return None


def get_current_user_optional(
        token: Optional[str] = Depends(oauth2_scheme_optional),
        db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except:
        return None