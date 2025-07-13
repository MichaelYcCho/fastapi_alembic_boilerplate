from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from app.repositories.user_repository import UserRepository
from app.repositories.jwt_repository import JwtRepository
from app.users.models.user import User
from app.schemas.auth import AuthRequest, TokenResponse, AccessTokenResponse
from app.schemas.user import UserResponse
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token, verify_token
from app.core.errors import AppError, AUTH_ERRORS, USERS_ERRORS
from app.core.config import settings
import time

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.jwt_repo = JwtRepository(db)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """사용자 인증을 수행합니다."""
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user
    
    async def login(self, auth_request: AuthRequest) -> TokenResponse:
        """사용자 로그인을 처리합니다."""
        user = await self.authenticate_user(auth_request.email, auth_request.password)
        if not user:
            raise AppError(AUTH_ERRORS["FAILED_AUTHENTICATE"])
        
        # 토큰 생성
        access_token = create_access_token({"id": user.id, "profile_name": user.profile_name})
        refresh_token = create_refresh_token({"id": user.id})
        
        # 리프레시 토큰 저장
        await self.update_refresh_token(user, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(user)
        )
    
    async def update_refresh_token(self, user: User, refresh_token: str) -> None:
        """리프레시 토큰을 업데이트합니다."""
        jwt_storage = await self.jwt_repo.get_jwt_storage_by_user_id(user.id)
        
        if not jwt_storage:
            raise AppError(AUTH_ERRORS["NOT_EXIST_JWT_STORAGE"])
        
        # 토큰 정보 파싱
        payload = verify_token(refresh_token, settings.JWT_REFRESH_SECRET)
        if not payload:
            raise AppError(AUTH_ERRORS["INVALID_REFRESH_TOKEN"])
        
        expired_at = payload.get("exp")
        hashed_token = hash_password(refresh_token)
        
        await self.jwt_repo.update_refresh_token(user.id, hashed_token, expired_at)
    
    async def refresh_access_token(self, refresh_token: str) -> AccessTokenResponse:
        """액세스 토큰을 재발급합니다."""
        # 리프레시 토큰 검증
        payload = verify_token(refresh_token, settings.JWT_REFRESH_SECRET)
        if not payload:
            raise AppError(AUTH_ERRORS["INVALID_REFRESH_TOKEN"])
        
        user_id = payload.get("id")
        if not user_id:
            raise AppError(AUTH_ERRORS["INVALID_REFRESH_TOKEN"])
        
        # 사용자 정보 조회
        user = await self.get_user_from_refresh_token(refresh_token, user_id)
        if not user:
            raise AppError(USERS_ERRORS["NOT_EXIST_USER"])
        
        # 새로운 액세스 토큰 생성
        access_token = create_access_token({"id": user.id, "profile_name": user.profile_name})
        
        return AccessTokenResponse(access_token=access_token)
    
    async def get_user_from_refresh_token(self, refresh_token: str, user_id: int) -> Optional[User]:
        """리프레시 토큰에서 사용자 정보를 가져옵니다."""
        user = await self.user_repo.get_user_by_id_with_jwt(user_id)
        if not user or not user.jwt_storage:
            return None
        
        if not user.jwt_storage.refresh_token:
            return None
        
        # 토큰 검증
        if verify_password(refresh_token, user.jwt_storage.refresh_token):
            return user
        
        return None
    
    async def logout(self, user: User) -> None:
        """사용자 로그아웃을 처리합니다."""
        jwt_storage = await self.jwt_repo.get_jwt_storage_by_user_id(user.id)
        if not jwt_storage:
            raise AppError(AUTH_ERRORS["NOT_EXIST_JWT_STORAGE"])
        
        await self.jwt_repo.remove_refresh_token(user.id) 