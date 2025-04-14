from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserResponse

get_user_router = APIRouter()

@get_user_router.get("/api/user", response_model=UserResponse)
async def get_current_user(
        user: User = Depends(get_current_user),
):
    return {"user": user}