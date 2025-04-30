from datetime import timedelta, datetime
from typing import Union, Any, Type, Optional

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.settings import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def hash_password(password) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(identity: Union[str, Any]) -> str:
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(identity),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(identity: Union[str, Any], db: Session) -> str:
    db.query(RefreshToken).filter(RefreshToken.user_id == int(identity)).delete()
    db.commit()

    expire = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(identity),
        "exp": expire,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

    refresh_token = RefreshToken(
        user_id=int(identity),
        refresh_token=encoded_jwt,
        created_at=datetime.now()
    )
    db.add(refresh_token)
    db.commit()

    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        unverified_payload = jwt.get_unverified_claims(token)
        token_type = unverified_payload.get("type")
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not decode token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type == "access":
        key = settings.ACCESS_TOKEN_SECRET_KEY
    elif token_type == "refresh":
        key = settings.REFRESH_TOKEN_SECRET_KEY
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return jwt.decode(token, key, algorithms=[settings.ALGORITHM])
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Type[User]:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Use access token for authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

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
        return db.query(User).filter(User.id == int(user_id)).first()
    except:
        return None

def admin_required(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access only"
        )
    return user
