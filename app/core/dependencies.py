from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .database.database import get_db
from app.users.models.user import User
from app.users.repositories.user_repository import UserRepository
from .security import verify_token
from .errors import AppError, AUTH_ERRORS
from .config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """현재 사용자 정보를 가져옵니다."""
    
    if not credentials:
        raise AppError(AUTH_ERRORS["MISSING_AUTHORIZATION_HEADER"])
    
    token = credentials.credentials
    if not token:
        raise AppError(AUTH_ERRORS["MISSING_JWT_TOKEN"])
    
    # 토큰 검증
    payload = verify_token(token, settings.JWT_ACCESS_SECRET)
    if not payload:
        raise AppError(AUTH_ERRORS["INVALID_ACCESS_TOKEN"])
    
    user_id = payload.get("id")
    if not user_id:
        raise AppError(AUTH_ERRORS["INVALID_ACCESS_TOKEN"])
    
    # 사용자 정보 조회
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_id(user_id)
    
    if not user:
        raise AppError(AUTH_ERRORS["INVALID_ACCESS_TOKEN"])
    
    return user 