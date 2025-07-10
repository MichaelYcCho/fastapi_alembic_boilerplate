from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .user import UserResponse

class AuthRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class AccessTokenResponse(BaseModel):
    access_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="리프레시 토큰") 