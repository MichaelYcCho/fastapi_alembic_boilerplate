from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.database import get_db
from app.core.dependencies import get_current_user
from app.users.models.user import User
from app.schemas.base import BaseResponse
from app.users.services.user_service import UserService
from app.users.dto.user_dto import UserCreateDto, UserUpdateDto, UserResponseDto, UserListResponseDto

users_router = APIRouter()

@users_router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreateDto,
    db: AsyncSession = Depends(get_db)
):
    """사용자 생성"""
    user_service = UserService(db)
    return await user_service.create_user(user_create)

@users_router.get("/", response_model=UserListResponseDto)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 목록 조회"""
    user_service = UserService(db)
    return await user_service.get_users_list(skip, limit)

@users_router.get("/{user_id}", response_model=UserResponseDto)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 상세 조회"""
    user_service = UserService(db)
    return await user_service.get_user_by_id(user_id)

@users_router.patch("/{user_id}", response_model=UserResponseDto)
async def update_user(
    user_id: int,
    user_update: UserUpdateDto,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 정보 업데이트"""
    user_service = UserService(db)
    
    # 현재 사용자 본인의 정보만 업데이트 가능 (또는 관리자)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    return await user_service.update_user(current_user, user_update)

@users_router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 삭제"""
    user_service = UserService(db)
    
    # 현재 사용자 본인의 정보만 삭제 가능 (또는 관리자)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    return await user_service.delete_user(current_user) 