from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.users.models.user import UserRole

# Request DTOs
class UserCreateDto(BaseModel):
    """사용자 생성 요청 DTO"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=4, description="비밀번호")
    profile_name: str = Field(..., min_length=1, max_length=30, description="프로필 이름")

class UserUpdateDto(BaseModel):
    """사용자 업데이트 요청 DTO"""
    profile_name: Optional[str] = Field(None, min_length=1, max_length=30)
    role: Optional[UserRole] = None

# Response DTOs
class UserResponseDto(BaseModel):
    """사용자 응답 DTO"""
    id: int
    email: str
    profile_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JwtStorageResponseDto(BaseModel):
    """JWT 저장소 응답 DTO"""
    id: int
    refresh_token: Optional[str] = None
    refresh_token_expired_at: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserWithJwtDto(UserResponseDto):
    """JWT 정보가 포함된 사용자 응답 DTO"""
    jwt_storage: Optional[JwtStorageResponseDto] = None
    
    class Config:
        from_attributes = True

class UserListResponseDto(BaseModel):
    """사용자 목록 응답 DTO"""
    users: List[UserResponseDto]
    total_count: int
    skip: int
    limit: int 