import logging
import uuid
from datetime import timedelta, datetime, UTC
from typing import Union, Optional

from fastapi import Depends, HTTPException, Header, Cookie, Request, Response
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.core.settings import settings
from app.models import RefreshToken, User
from app.models.tokens_blacklist import TokenBlacklist

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def set_auth_cookies(response: Response, tokens: dict):    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {tokens['access_token']}",
        httponly=True,
        secure=settings.HTTPS_ENABLED,
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {tokens['refresh_token']}",
        httponly=True,
        secure=settings.HTTPS_ENABLED,
        samesite="lax",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


def delete_auth_cookies(response: Response):
    cookie_params = {
        "secure": settings.HTTPS_ENABLED,
        "httponly": True,
        "samesite": "lax",
        "path": "/",
    }
    
    response.delete_cookie(key="access_token", **cookie_params)
    response.delete_cookie(key="refresh_token", **cookie_params)


def hash_password(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(identity: Union[str, int]) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    to_encode = {
        "sub": str(identity),
        "exp": expire,
        "type": "access",
        "jti": jti
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


def add_to_blacklist(jti: str, exp: int, db: Session):
    expires_at = datetime.fromtimestamp(exp, tz=UTC)
    blacklist_entry = TokenBlacklist(expires_at=expires_at, jti=jti)
    db.add(blacklist_entry)
    db.commit()
    
    
def is_blacklisted(jti: str, db: Session) -> bool:
    return(db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()) is not None


def decode_token(token: str) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        unverified_payload = jwt.get_unverified_claims(token)
        token_type = unverified_payload.get("type")
    except JWTError as e:
        logger.error(f"Could not decode token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
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
    except (JWTClaimsError, JWTError):
        logger.warning("Token verification failed (claims or JWT error).")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_from_request(
        authorization: Optional[str] = Header(None, alias="Authorization"),
        access_token_cookie: Optional[str] = Cookie(None, alias="access_token")
) -> Optional[str]:
    token = None
    if authorization:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    elif access_token_cookie:
        token = access_token_cookie[7:] if access_token_cookie.startswith("Bearer ") else access_token_cookie
    return token


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(get_token_from_request),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
    except HTTPException:
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Use access token for authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    jti = payload.get('jti')
    if is_blacklisted(jti, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def get_current_user_optional(
        db: Session = Depends(get_db),
        token: str = Depends(get_token_from_request)

) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)        
        user_id = payload.get("sub")
        jti = payload.get('jti')
        
        if not user_id or payload.get("type") != "access" or is_blacklisted(jti, db):
            return None
        
        return db.query(User).filter(User.id == int(user_id)).first()
    except HTTPException:
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


def cleanup_expired_tokens(db: Session):
    now = datetime.now(UTC)
    deleted_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < now,
    ).delete()
    deleted_blacklist_count = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at < now,
    ).delete()
    db.commit()

    return deleted_count + deleted_blacklist_count
