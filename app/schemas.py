from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleSchema(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
    roles: List[RoleSchema] = []

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class DummyTokenRequest(BaseModel):
    user_id: int
