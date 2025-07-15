from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.repositories.jwt_repository import JwtRepository
from app.users.models.user import User
from app.core.security import hash_password
from app.core.errors import AppError, USERS_ERRORS
from app.users.repositories.user_repository import UserRepository
from app.users.dto.user_dto import UserCreateDto, UserUpdateDto, UserResponseDto, UserListResponseDto
import logging

logger = logging.getLogger(__name__)

class UserService:
    """사용자 비즈니스 로직을 담당하는 Service 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.jwt_repository = JwtRepository(db)
    
    async def create_user(self, user_create: UserCreateDto) -> dict:
        """사용자를 생성합니다."""
        try:
            # 이메일 중복 확인
            existing_user = await self.user_repository.get_user_by_email(user_create.email)
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
            
            user = await self.user_repository.create_user(user_data)
            
            # JWT 저장소 생성
            await self.jwt_repository.create_jwt_storage(user.id)
            
            logger.info(f"[CreateUser] Success: {user.email}")
            return {
                "id": user.id,
                "message": "success",
            }
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[CreateUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_CREATE_USER"])
    
    async def get_user_by_id(self, user_id: int) -> UserResponseDto:
        """사용자를 ID로 조회합니다."""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise AppError(USERS_ERRORS["NOT_EXIST_USER"])
            
            return UserResponseDto.model_validate(user)
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[GetUserById] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_GET_USER_PROFILE"])
    
    async def get_users_list(self, skip: int = 0, limit: int = 100) -> UserListResponseDto:
        """사용자 목록을 조회합니다."""
        try:
            users = await self.user_repository.get_users_list(skip, limit)
            total_count = await self.user_repository.get_users_count()
            
            user_dto_list = [UserResponseDto.model_validate(user) for user in users]
            
            return UserListResponseDto(
                users=user_dto_list,
                total_count=total_count,
                skip=skip,
                limit=limit
            )
        
        except Exception as e:
            logger.error(f"[GetUsersList] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_GET_USER_PROFILE"])
    
    async def update_user(self, user: User, update_dto: UserUpdateDto) -> UserResponseDto:
        """사용자 정보를 업데이트합니다."""
        try:
            if update_dto.profile_name is not None:
                user.profile_name = update_dto.profile_name
            
            if update_dto.role is not None:
                user.role = update_dto.role
            
            updated_user = await self.user_repository.update_user(user)
            return UserResponseDto.model_validate(updated_user)
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[UpdateUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_UPDATE_USER"])
    
    async def delete_user(self, user: User) -> dict:
        """사용자를 삭제합니다."""
        try:
            await self.user_repository.delete_user(user)
            logger.info(f"[DeleteUser] Success: {user.email}")
            return {"message": "success"}
        
        except AppError:
            raise
        except Exception as e:
            logger.error(f"[DeleteUser] Error: {str(e)}")
            raise AppError(USERS_ERRORS["FAILED_DELETE_USER"]) 