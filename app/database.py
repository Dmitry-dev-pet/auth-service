from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import Settings, get_settings


def get_engine(settings: Settings = Depends(get_settings)):
    return create_async_engine(settings.database_url, echo=False)


def get_session_maker(engine=Depends(get_engine)):
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session(
    async_session_maker=Depends(get_session_maker),
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
