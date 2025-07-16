import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.core.database.database import Base, get_db
from app.core.database.database_manager import DatabaseManager

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_fastapi_alembic_boilerplate"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_db):
    async_session = sessionmaker(
        test_db, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def client():
    async def override_get_db():
        # Mock database session for testing
        return AsyncMock()
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }