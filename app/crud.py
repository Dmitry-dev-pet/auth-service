from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas


async def get_user(db: AsyncSession, user_id: int):
    """
    Получение пользователя по его ID.
    """
    result = await db.execute(
        select(models.User)
        .filter(models.User.id == user_id)
        .options(selectinload(models.User.roles))
    )
    return result.scalars().first()


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    """
    Получение пользователя по его Telegram ID.
    """
    result = await db.execute(
        select(models.User)
        .filter(models.User.telegram_id == telegram_id)
        .options(selectinload(models.User.roles))
    )
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


async def get_role_by_name(db: AsyncSession, name: str):
    """
    Получение роли по ее имени.
    """
    result = await db.execute(select(models.Role).filter(models.Role.name == name))
    return result.scalars().first()


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Получение списка ролей.
    """
    result = await db.execute(select(models.Role).offset(skip).limit(limit))
    return result.scalars().all()


async def create_role(db: AsyncSession, role: schemas.RoleCreate) -> models.Role:
    """
    Создание новой роли.
    """
    db_role = models.Role(**role.model_dump())
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def add_role_to_user(db: AsyncSession, user: models.User, role: models.Role):
    """
    Добавление роли пользователю.
    """
    user.roles.append(role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
