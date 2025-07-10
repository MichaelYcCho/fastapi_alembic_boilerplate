from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..repositories.user_repository import UserRepository
from ..repositories.jwt_repository import JwtRepository
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..schemas.base import BaseResponse
from ..core.security import hash_password
from ..core.errors import AppError, USERS_ERRORS
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.jwt_repo = JwtRepository(db)
    
    async def create_user(self, user_create: UserCreate) -> BaseResponse:
        """사용자를 생성합니다."""
        try:
            # 이메일 중복 확인
            existing_user = await self.user_repo.get_user_by_email(user_create.email)
            if existing_user:
                raise AppError(USERS_ERRORS["USER_EMAIL_ALREADY_EXIST"])
            
            # 비밀번호 해시화
            hashed_password = hash_password(user_create.password)
            
            # 사용자 생성
            user_data = {
                "email": user_create.email,
                "password": hashed_password,
                "profile_name": user_create.profile_name
            }
            
            user = await self.user_repo.create_user(user_data)
            
            # JWT 저장소 생성
            await self.jwt_repo.create_jwt_storage(user.id)
            
            logger.info(f"[CreateUser] Success: {user.email}")
            return BaseResponse(message="success")
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[CreateUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_CREATE_USER"])
    
    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """사용자를 ID로 조회합니다."""
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise AppError(USERS_ERRORS["NOT_EXIST_USER"])
            
            return UserResponse.from_orm(user)
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[GetUserById] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_GET_USER_PROFILE"])
    
    async def get_users_list(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """사용자 목록을 조회합니다."""
        try:
            users = await self.user_repo.get_users_list(skip, limit)
            return [UserResponse.from_orm(user) for user in users]
        
        except Exception as e:
            logger.error(f"[GetUsersList] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_GET_USER_PROFILE"])
    
    async def update_user(self, user: User, user_update: UserUpdate) -> UserResponse:
        """사용자 정보를 업데이트합니다."""
        try:
            if user_update.profile_name is not None:
                user.profile_name = user_update.profile_name
            
            if user_update.role is not None:
                user.role = user_update.role
            
            updated_user = await self.user_repo.update_user(user)
            return UserResponse.from_orm(updated_user)
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[UpdateUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_UPDATE_USER"])
    
    async def delete_user(self, user: User) -> BaseResponse:
        """사용자를 삭제합니다."""
        try:
            await self.user_repo.delete_user(user)
            logger.info(f"[DeleteUser] Success: {user.email}")
            return BaseResponse(message="success")
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[DeleteUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_DELETE_USER"]) 