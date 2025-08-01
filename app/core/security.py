import uuid
from datetime import timedelta, datetime, UTC
from typing import Union, Optional

from fastapi import Depends, HTTPException, Header, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.settings import settings
from app.models import RefreshToken, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def hash_password(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(identity: Union[str, int]) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(identity),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(identity: Union[str, int], db: Session, request: Request) -> str:

    jti = str(uuid.uuid4())
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(identity),
        "exp": expire_at,
        "type": "refresh",
        "jti": jti,
    }
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

    refresh_token_db_entry = RefreshToken(
        user_id=int(identity),
        jti=jti,
        refresh_token=encoded_jwt,
        created_at=datetime.now(UTC),
        expires_at=expire_at,
        last_used_at=datetime.now(UTC),
        is_revoked=False,
        device_info=request.headers.get("User-Agent"),
        ip_address=request.client.host,
    )
    db.add(refresh_token_db_entry)
    db.commit()
    db.refresh(refresh_token_db_entry)

    return encoded_jwt


def decode_token(token: str) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        unverified_payload = jwt.get_unverified_claims(token)
        token_type = unverified_payload.get("type")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode token (JWT Error)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error getting unverified claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode token (general error)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type == "access":
        key = settings.ACCESS_TOKEN_SECRET_KEY
    elif token_type == "refresh":
        key = settings.REFRESH_TOKEN_SECRET_KEY
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return jwt.decode(token, key, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed (claims error)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed (JWT error)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed (general error)",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
        db: Session = Depends(get_db),
        authorization: Optional[str] = Header(None, alias="Authorization"),
        access_token_cookie: Optional[str] = Cookie(None, alias="access_token")
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = None
    if authorization:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    elif access_token_cookie:
        token = access_token_cookie[7:] if access_token_cookie.startswith("Bearer ") else access_token_cookie

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
    except HTTPException as e:
        print(f"Unexpected error during token decoding: {e}")
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Use access token for authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # noinspection PyTypeChecker
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def get_current_user_optional(
        db: Session = Depends(get_db),
        authorization: Optional[str] = Header(None, alias="Authorization"),
        access_token_cookie: Optional[str] = Cookie(None, alias="access_token")

) -> Optional[User]:
    token = None
    if authorization:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    elif access_token_cookie:
        token = access_token_cookie[7:] if access_token_cookie.startswith("Bearer ") else access_token_cookie

    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            return None
        # noinspection PyTypeChecker
        return db.query(User).filter(User.id == int(user_id)).first()
    except HTTPException:
        return None
    except Exception as e:
        print(f"DEBUG: Unexpected error in get_current_user_optional: {e}")
        return None


def admin_required(user=Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user


def issue_tokens(user_id: int, db: Session, request: Request) -> dict:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id, db, request)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
