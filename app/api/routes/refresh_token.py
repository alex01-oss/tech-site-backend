from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token, oauth2_scheme, decode_token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user_schema import RefreshTokenResponse

refresh_token_router = APIRouter()

@refresh_token_router.post("/api/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if not db_token:
            raise HTTPException(status_code=401, detail="Refresh token not found")

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_access_token(identity=user.id)

        return {"token": new_access_token}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e