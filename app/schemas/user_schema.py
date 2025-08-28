from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.encryption import encryption_service


class UserData(BaseModel):
    id: int
    role: str
    full_name: str
    email: str
    phone: str

    @field_validator('email', 'phone', mode='before')
    def decrypt_sensitive_fields(cls, value: Optional[str]):
        if value:
            return encryption_service.decrypt_data(value)
        return value

    class Config:
        from_attributes = True


class TokenBundle(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    password: Optional[str] = Field(None, min_length=8)


class MessageResponse(BaseModel):
    message: str


class AuthResponse(TokenBundle):
    user: UserData
    message: str


class UserResponse(BaseModel):
    user: UserData
