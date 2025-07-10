from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from ..models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=4, description="비밀번호")
    profile_name: str = Field(..., min_length=1, max_length=30, description="프로필 이름")

class UserUpdate(BaseModel):
    profile_name: Optional[str] = Field(None, min_length=1, max_length=30)
    role: Optional[UserRole] = None

class UserResponse(BaseModel):
    id: int
    email: str
    profile_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JwtStorageResponse(BaseModel):
    id: int
    refresh_token: Optional[str] = None
    refresh_token_expired_at: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserWithJWT(UserResponse):
    jwt_storage: Optional[JwtStorageResponse] = None
    
    class Config:
        from_attributes = True 