from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None
    name: str | None = None
    language_code: str | None = "ru"


class UserCreate(UserBase):
    pass


class UserSchema(UserBase):
    id: int
    is_bot: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class DummyTokenRequest(BaseModel):
    user_id: int
