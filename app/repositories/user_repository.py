from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from ..models.user import User
from ..models.jwt_storage import JwtStorage

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id_with_jwt(self, user_id: int) -> Optional[User]:
        """ID로 사용자를 JWT 정보와 함께 조회합니다."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.jwt_storage))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email_with_password(self, email: str) -> Optional[User]:
        """이메일로 사용자를 비밀번호와 함께 조회합니다."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: dict) -> User:
        """사용자를 생성합니다."""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user: User) -> User:
        """사용자 정보를 업데이트합니다."""
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user: User) -> None:
        """사용자를 삭제합니다."""
        await self.db.delete(user)
        await self.db.commit()
    
    async def get_users_list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 목록을 조회합니다."""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_users_count(self) -> int:
        """전체 사용자 수를 조회합니다."""
        result = await self.db.execute(
            select(func.count(User.id))
        )
        return result.scalar() 