from fastapi import APIRouter
from fastapi.params import Depends

from app.core.security import get_current_user, create_access_token
from app.models.user import User
from app.schemas.user_schema import RefreshTokenResponse

refresh_token_router = APIRouter()

@refresh_token_router.post("/api/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    new_access_token = create_access_token(identity=current_user)
    
    return {
        "token": new_access_token
    }