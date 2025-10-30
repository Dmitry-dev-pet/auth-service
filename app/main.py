from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    AUTH_JWT_SECRET_KEY: str
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TELEGRAM_BOT_TOKEN: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


engine = create_async_engine(get_settings().DATABASE_URL)
DBSession = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with DBSession() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown


app = FastAPI(lifespan=lifespan)


from fastapi import HTTPException, APIRouter
from . import crud, schemas, security

router = APIRouter()


@router.post("/auth/dummy-token", response_model=schemas.Token)
async def dummy_auth(request: schemas.DummyTokenRequest):
    """
    Генерирует JWT токен для указанного user_id.
    Только для разработки и тестирования.
    """
    access_token = security.create_access_token(
        data={"sub": str(request.user_id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.UserSchema)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя.
    """
    db_user = await crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this Telegram ID already registered")
    return await crud.create_user(db=db, user=user)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

app.include_router(router)