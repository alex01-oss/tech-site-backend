from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserData


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str


class RegisterResponse(BaseModel):
    message: str
    user: UserData
    access_token: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserData
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str


class UpdateUserRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2)
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=8, max_length=20)
    password: str | None = Field(None, min_length=6)
