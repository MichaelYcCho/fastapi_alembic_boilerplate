from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from ..models.jwt_storage import JwtStorage
from ..models.user import User

class JwtRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_jwt_storage_by_user_id(self, user_id: int) -> Optional[JwtStorage]:
        """사용자 ID로 JWT 저장소를 조회합니다."""
        result = await self.db.execute(
            select(JwtStorage).where(JwtStorage.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_jwt_storage(self, user_id: int) -> JwtStorage:
        """JWT 저장소를 생성합니다."""
        jwt_storage = JwtStorage(user_id=user_id)
        self.db.add(jwt_storage)
        await self.db.commit()
        await self.db.refresh(jwt_storage)
        return jwt_storage
    
    async def update_refresh_token(self, user_id: int, refresh_token: str, expired_at: int) -> None:
        """리프레시 토큰을 업데이트합니다."""
        await self.db.execute(
            update(JwtStorage)
            .where(JwtStorage.user_id == user_id)
            .values(
                refresh_token=refresh_token,
                refresh_token_expired_at=expired_at
            )
        )
        await self.db.commit()
    
    async def remove_refresh_token(self, user_id: int) -> None:
        """리프레시 토큰을 제거합니다."""
        await self.db.execute(
            update(JwtStorage)
            .where(JwtStorage.user_id == user_id)
            .values(
                refresh_token=None,
                refresh_token_expired_at=None
            )
        )
        await self.db.commit() 