from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import decode_token, oauth2_scheme
from app.models.refresh_token import RefreshToken
from app.schemas.user_schema import LogoutResponse

logout_router = APIRouter()

@logout_router.post("/api/logout", response_model=LogoutResponse)
async def logout(
    refresh_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_token(refresh_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db.query(RefreshToken).filter_by(
        user_id=user_id,
        refresh_token = refresh_token
    ).delete()
    db.commit()

    return LogoutResponse(
        message="Successfully logged out",
    )
