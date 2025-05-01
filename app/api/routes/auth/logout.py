from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import decode_token, oauth2_scheme
from app.models.refresh_token import RefreshToken
from app.schemas.user_schema import LogoutResponse, LogoutRequest

logout_router = APIRouter()


@logout_router.post("/api/logout", response_model=LogoutResponse)
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
        refresh_token=logout_data.refreshToken
    ).delete()
    db.commit()

    if not refresh_token_entry:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    return LogoutResponse(
        message="Successfully logged out",
    )