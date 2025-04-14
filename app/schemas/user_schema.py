from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: User
    token: str
    refreshToken: str

class RegisterResponse(BaseModel):
    user: User
    token: str
    refreshToken: str

class RefreshTokenResponse(BaseModel):
    token: str

class LogoutResponse(BaseModel):
    message: str

class UserResponse(BaseModel):
    user: User