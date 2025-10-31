from pydantic import BaseModel, ConfigDict


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class DummyTokenRequest(BaseModel):
    user_id: int


# Role
class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# User
class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    roles: list[Role] = []

    model_config = ConfigDict(from_attributes=True)


class UserRole(BaseModel):
    role_id: int
