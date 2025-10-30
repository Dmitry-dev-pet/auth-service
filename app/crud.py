from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    """
    Получение пользователя по его Telegram ID.
    """
    result = await db.execute(select(models.User).filter(models.User.telegram_id == telegram_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """
    Создание нового пользователя.
    """
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
