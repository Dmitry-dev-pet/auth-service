from typing import Annotated, List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .config import Settings, get_settings
from .database import get_async_session
from .security import create_access_token

app = FastAPI(
    title="Auth Service",
    description="Сервис для аутентификации и авторизации пользователей.",
    version="0.1.0",
)

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

router = APIRouter()


@router.post(
    "/internal/users",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя (внутренний эндпоинт)",
    tags=["Internal"],
)
async def create_user(user: schemas.UserCreate, db: DBSession):
    """
    Создает нового пользователя в системе.
    - **telegram_id**: ID пользователя в Telegram.
    - **username**: Имя пользователя в Telegram.
    - **first_name**: Имя.
    - **last_name**: Фамилия (опционально).
    """
    db_user = await crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this telegram_id already exists",
        )
    return await crud.create_user(db=db, user=user)


@router.get(
    "/internal/users",
    response_model=List[schemas.User],
    summary="Получить список пользователей (внутренний эндпоинт)",
    tags=["Internal"],
)
async def read_users(db: DBSession, skip: int = 0, limit: int = 100):
    """
    Возвращает список пользователей с пагинацией.
    """
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@router.post(
    "/auth/dummy-token",
    response_model=schemas.Token,
    summary="Сгенерировать JWT токен (dummy)",
    tags=["Auth"],
)
async def dummy_auth(
    request: schemas.DummyTokenRequest, settings: Annotated[Settings, Depends(get_settings)]
):
    """
    Генерирует JWT токен для указанного `user_id`.
    **Только для разработки и тестирования.**
    """
    # TODO: Проверить, что эндпоинт недоступен в prod
    access_token = create_access_token(
        data={"sub": str(request.user_id)}, settings=settings
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/internal/roles",
    response_model=schemas.Role,
    status_code=status.HTTP_201_CREATED,
    summary="Создать роль (внутренний эндпоинт)",
    tags=["Internal"],
)
async def create_role(role: schemas.RoleCreate, db: DBSession):
    """
    Создает новую роль в системе.
    """
    db_role = await crud.get_role_by_name(db, name=role.name)
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists",
        )
    return await crud.create_role(db=db, role=role)


@router.get(
    "/internal/roles",
    response_model=List[schemas.Role],
    summary="Получить список ролей (внутренний эндпоинт)",
    tags=["Internal"],
)
async def read_roles(db: DBSession, skip: int = 0, limit: int = 100):
    """
    Возвращает список ролей с пагинацией.
    """
    roles = await crud.get_roles(db, skip=skip, limit=limit)
    return roles


@router.post(
    "/internal/users/{user_id}/roles",
    response_model=schemas.User,
    summary="Добавить роль пользователю (внутренний эндпоинт)",
    tags=["Internal"],
)
async def add_role_to_user(
    user_id: int, user_role: schemas.UserRole, db: DBSession
):
    """
    Назначает роль указанному пользователю.
    """
    user = await crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = await crud.get_role(db, role_id=user_role.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return await crud.add_role_to_user(db=db, user=user, role=role)


app.include_router(router)
