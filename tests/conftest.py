import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base
from app.main import get_settings, Settings
from functools import lru_cache

DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/test"

@lru_cache
def get_test_settings() -> Settings:
    return Settings()

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        
        TestingSessionLocal = sessionmaker(
            bind=connection, class_=AsyncSession, expire_on_commit=False
        )
        session = TestingSessionLocal()
        
        try:
            yield session
        finally:
            await session.close()
            await connection.rollback()

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def test_app(db_session: AsyncSession) -> FastAPI:
    """Create a test app with overridden dependencies."""
    
    async def get_test_db_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = get_test_db_override
    
    return app

@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async client for testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
