import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def test_healthcheck(client: AsyncClient):
    response = await client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/users/",
        json={"telegram_id": 123, "username": "testuser"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 123
    assert data["username"] == "testuser"
    assert "id" in data


async def test_create_role(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/roles/",
        json={"name": "student", "description": "A student role"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "student"
    assert "id" in data


async def test_add_role_to_user(client: AsyncClient, db_session: AsyncSession):
    # First, create a user and a role
    await client.post("/api/users/", json={"telegram_id": 456, "username": "anotheruser"})
    await client.post("/api/roles/", json={"name": "mentor"})

    # Then, add the role to the user
    response = await client.post("/api/users/456/roles?role_name=mentor")
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 456
    
    # Check that the role is in the user's roles
    role_names = [role["name"] for role in data["roles"]]
    assert "mentor" in role_names