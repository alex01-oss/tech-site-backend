from typing import Optional

from pydantic import BaseModel


class UserData(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserData


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    message: str
    user: UserData
    accessToken: str
    refreshToken: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserData
    accessToken: str
    refreshToken: str


class RefreshTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str
