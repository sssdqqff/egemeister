import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.user import User, UserRole


async def create_api_user(db_session, role=UserRole.USER, username=None):
    user = User(
        first_name="User API test",
        role=role,
        username=username,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def user_api_client(db_session):
    original_overrides = app.dependency_overrides.copy()
    state = {"user": None}

    async def override_get_db():
        yield db_session

    async def override_current_user():
        return state["user"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client, state
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.mark.asyncio
async def test_regular_user_cannot_list_users(
    db_session,
    user_api_client,
):
    client, state = user_api_client
    state["user"] = await create_api_user(db_session)

    response = await client.get("/users")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_list_users(
    db_session,
    user_api_client,
):
    client, state = user_api_client
    state["user"] = await create_api_user(
        db_session,
        role=UserRole.ADMIN,
    )

    response = await client.get("/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_regular_user_cannot_update_another_user(
    db_session,
    user_api_client,
):
    client, state = user_api_client
    state["user"] = await create_api_user(db_session)
    target = await create_api_user(db_session, username="target_user")

    response = await client.patch(
        f"/users/{target.id}",
        json={"username": "changed_user"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(
    db_session,
    user_api_client,
):
    client, state = user_api_client
    admin = await create_api_user(
        db_session,
        role=UserRole.ADMIN,
    )
    state["user"] = admin

    response = await client.delete(f"/users/{admin.id}")

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot deactivate yourself"

    await db_session.refresh(admin)
    assert admin.is_active is True


@pytest.mark.asyncio
async def test_user_can_update_own_username(
    db_session,
    user_api_client,
):
    client, state = user_api_client
    user = await create_api_user(db_session, username="old_username")
    state["user"] = user

    response = await client.patch(
        "/users/me",
        json={"username": "new_username"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "new_username"

    await db_session.refresh(user)
    assert user.username == "new_username"