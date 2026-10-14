from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.user import User


async def create_user(db_session, first_name="Session API user"):
    user = User(first_name=first_name)
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def session_api_client(db_session):
    original_overrides = app.dependency_overrides.copy()
    current_user = SimpleNamespace(id=None)

    async def override_get_db():
        yield db_session

    async def override_current_user():
        return current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client, current_user
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.mark.asyncio
async def test_create_and_get_session_through_api(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    response = await client.post(
        "/sessions",
        json={"type": "practice"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user.id
    assert data["type"] == "practice"
    assert data["status"] == "in_progress"

    detail = await client.get(f"/sessions/{data['id']}")

    assert detail.status_code == 200
    assert detail.json()["id"] == data["id"]


@pytest.mark.asyncio
async def test_user_cannot_get_another_users_session(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    owner = await create_user(db_session, "Session owner")
    another_user = await create_user(db_session, "Another user")
    current_user.id = owner.id

    response = await client.post(
        "/sessions",
        json={"type": "practice"},
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    current_user.id = another_user.id
    response = await client.get(f"/sessions/{session_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


@pytest.mark.asyncio
async def test_finish_session_through_api(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    created = await client.post(
        "/sessions",
        json={"type": "practice"},
    )
    assert created.status_code == 201
    session_id = created.json()["id"]

    response = await client.patch(f"/sessions/{session_id}/finish")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["finished_at"] is not None

    second_response = await client.patch(
        f"/sessions/{session_id}/finish"
    )
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_session_summary_through_api(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    created = await client.post(
        "/sessions",
        json={"type": "practice"},
    )
    assert created.status_code == 201
    session_id = created.json()["id"]

    response = await client.get(f"/sessions/{session_id}/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "in_progress"
    assert data["total_attempts"] == 0
    assert data["correct_attempts"] == 0
    assert data["accuracy"] == 0.0


@pytest.mark.asyncio
async def test_session_endpoint_requires_authentication(
    session_api_client,
):
    client, _ = session_api_client
    app.dependency_overrides.pop(get_current_user, None)

    response = await client.get("/sessions")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_session_accepts_configuration(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    response = await client.post(
        "/sessions",
        json={
            "type": "practice",
            "title": "Тренировка по информатике",
            "time_limit_seconds": 600,
            "difficulty": "hard",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тренировка по информатике"
    assert data["time_limit_seconds"] == 600
    assert data["difficulty"] == "hard"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"status": "completed"},
        {"finished_at": "2026-01-01T00:00:00Z"},
    ],
)
async def test_session_patch_cannot_change_lifecycle_fields(
    db_session,
    session_api_client,
    payload,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    created = await client.post("/sessions", json={"type": "practice"})
    assert created.status_code == 201
    session_id = created.json()["id"]

    response = await client.patch(
        f"/sessions/{session_id}",
        json=payload,
    )

    assert response.status_code == 422

    detail = await client.get(f"/sessions/{session_id}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "in_progress"
    assert detail.json()["finished_at"] is None


@pytest.mark.asyncio
async def test_session_title_can_be_updated(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    created = await client.post("/sessions", json={"type": "practice"})
    session_id = created.json()["id"]

    response = await client.patch(
        f"/sessions/{session_id}",
        json={"title": "Повторение сложных тем"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Повторение сложных тем"
    assert response.json()["status"] == "in_progress"
    assert response.json()["finished_at"] is None


@pytest.mark.asyncio
async def test_abandon_session_through_api(
    db_session,
    session_api_client,
):
    client, current_user = session_api_client
    user = await create_user(db_session)
    current_user.id = user.id

    created = await client.post("/sessions", json={"type": "practice"})
    assert created.status_code == 201
    session_id = created.json()["id"]

    response = await client.patch(
        f"/sessions/{session_id}/abandon"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "abandoned"
    assert response.json()["finished_at"] is not None

    second_response = await client.patch(
        f"/sessions/{session_id}/abandon"
    )
    assert second_response.status_code == 409