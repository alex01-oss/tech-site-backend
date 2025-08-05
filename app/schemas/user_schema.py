from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str

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
    full_name: str | None = Field(None, min_length=2)
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=8, max_length=20)
    password: str | None = Field(None, min_length=6)


class MessageResponse(BaseModel):
    message: str


class TokenResponse(TokenBundle):
    message: str


class UserResponse(BaseModel):
    user: UserData
