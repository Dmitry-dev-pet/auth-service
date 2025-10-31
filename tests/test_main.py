import pytest
from httpx import AsyncClient

from app.schemas import Role, User


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """
    Проверяет успешное создание нового пользователя.
    """
    response = await client.post(
        "/internal/users",
        json={
            "telegram_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 201
    user = User.model_validate(response.json())
    assert user.telegram_id == 12345
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_create_existing_user(client: AsyncClient):
    """
    Проверяет, что создание пользователя с уже существующим telegram_id возвращает ошибку.
    """
    await client.post(
        "/internal/users",
        json={
            "telegram_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    response = await client.post(
        "/internal/users",
        json={
            "telegram_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_read_users(client: AsyncClient):
    """
    Проверяет получение списка пользователей и наличие в нем созданного пользователя.
    """
    # Create a user to find
    user_response = await client.post(
        "/internal/users",
        json={"telegram_id": 54321, "username": "findme"},
    )
    assert user_response.status_code == 201
    created_user_id = user_response.json()["id"]

    response = await client.get("/internal/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

    # Check if the created user is in the list
    found = any(user["id"] == created_user_id for user in users)
    assert found, "Created user not found in the list"


@pytest.mark.asyncio
async def test_dummy_auth(client: AsyncClient):
    """
    Проверяет, что эндпоинт для разработки /auth/dummy-token успешно генерирует токен.
    """
    response = await client.post("/auth/dummy-token", json={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_create_role(client: AsyncClient):
    """
    Проверяет успешное создание новой роли.
    """
    response = await client.post("/internal/roles", json={"name": "admin"})
    assert response.status_code == 201
    role = Role.model_validate(response.json())
    assert role.name == "admin"


@pytest.mark.asyncio
async def test_create_existing_role(client: AsyncClient):
    """
    Проверяет, что создание роли с уже существующим именем возвращает ошибку.
    """
    await client.post("/internal/roles", json={"name": "admin"})
    response = await client.post("/internal/roles", json={"name": "admin"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_read_roles(client: AsyncClient):
    """
    Проверяет получение списка ролей и наличие в нем созданной роли.
    """
    await client.post("/internal/roles", json={"name": "test_role"})
    response = await client.get("/internal/roles")
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert any(role["name"] == "test_role" for role in roles)


@pytest.mark.asyncio
async def test_add_role_to_user(client: AsyncClient):
    """
    Проверяет успешное назначение роли пользователю.
    """
    user_resp = await client.post(
        "/internal/users", json={"telegram_id": 999, "username": "user_with_role"}
    )
    user_id = user_resp.json()["id"]

    role_resp = await client.post("/internal/roles", json={"name": "super_admin"})
    role_id = role_resp.json()["id"]

    response = await client.post(
        f"/internal/users/{user_id}/roles", json={"role_id": role_id}
    )
    assert response.status_code == 200
    user = User.model_validate(response.json())
    assert len(user.roles) == 1
    assert user.roles[0].name == "super_admin"
