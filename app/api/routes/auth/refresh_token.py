from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token, decode_token, oauth2_scheme, create_refresh_token
from app.models.refresh_token import RefreshToken
from app.schemas.user_schema import RefreshTokenResponse

refresh_token_router = APIRouter()


@refresh_token_router.post("/api/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
        db: Session = Depends(get_db),
        refresh_token: str = Depends(oauth2_scheme)
):
    payload = decode_token(refresh_token)
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if not user_id or token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_record = db.query(RefreshToken).filter(
        RefreshToken.user_id == int(user_id),
        RefreshToken.refresh_token == refresh_token
    ).first()

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or revoked token")

    db.delete(token_record)
    db.commit()

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id, db)

    return RefreshTokenResponse(
        accessToken=new_access_token,
        refreshToken=new_refresh_token,
        token_type="bearer"
    )
