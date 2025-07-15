from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.database import get_db
from app.auth.services.auth_service import AuthService
from app.auth.dto.auth import AuthRequest, TokenResponse, AccessTokenResponse, RefreshTokenRequest
from app.core.dependencies import get_current_user
from app.dto.base_response import BaseResponse
from app.users.models.user import User

auth_router = APIRouter()

@auth_router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    auth_request: AuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """사용자 로그인"""
    auth_service = AuthService(db)
    return await auth_service.login(auth_request)

@auth_router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """액세스 토큰 재발급"""
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(refresh_request.refresh_token)

@auth_router.delete("/sign-out", response_model=BaseResponse)
async def sign_out(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 로그아웃"""
    auth_service = AuthService(db)
    await auth_service.logout(current_user)
    return BaseResponse(message="success") 