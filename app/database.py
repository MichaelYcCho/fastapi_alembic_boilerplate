from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .database_manager import db_manager, Base

# DatabaseManager를 통한 동기 엔진 및 세션
sync_engine = db_manager.engine
SessionLocal = db_manager.SessionLocal

# Async engine for async operations (SSH 터널링 고려)
def get_async_database_url():
    """SSH 터널링을 고려한 비동기 데이터베이스 URL 생성"""
    if db_manager.ssh_tunnel_active:
        # SSH 터널링이 활성화된 경우 localhost:5433으로 연결
        return f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@localhost:{settings.SSH_LOCAL_PORT}/{settings.DB_NAME}"
    else:
        # 직접 연결 또는 SSH 터널링이 비활성화된 경우
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    get_async_database_url(),
    echo=True if settings.NODE_ENV == "dev" else False,
)

# Session makers
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 동기 세션 의존성
def get_sync_db():
    return db_manager.get_db_session() 