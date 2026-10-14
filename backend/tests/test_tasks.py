from types import SimpleNamespace

from app.models.user import UserRole

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.dependencies import get_current_user
from app.routers.task_router import get_task_service


class FakeTaskService:
    async def get_all_tasks(self):
        return [{
            "id": 1,
            "condition": "Сколько единиц в двоичной записи числа 13?",
            "answer": "3",
            "difficulty": "easy",
            "is_active": True,
            "topic_id": 1,
            "prototype_id": 1,
        }]

    async def create_task(self, task_data):
        return {
            "id": 2,
            "condition": task_data.condition,
            "answer": task_data.answer,
            "difficulty": task_data.difficulty,
            "is_active": True,
            "topic_id": task_data.topic_id,
            "prototype_id": task_data.prototype_id,
        }


@pytest.fixture
def test_app():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_task_service] = FakeTaskService
    yield app
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture
def authenticated_app(test_app):
    test_app.dependency_overrides[get_current_user] = lambda: object()
    return test_app


@pytest.mark.asyncio
async def test_get_tasks_does_not_return_answer(authenticated_app):
    async with AsyncClient(
        transport=ASGITransport(app=authenticated_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "answer" not in response.json()[0]


@pytest.mark.asyncio
async def test_get_tasks_requires_authentication(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/tasks")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_forbidden_for_regular_user(test_app):
    test_app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(role="user")
    )

    payload = {
        "condition": "Сколько будет 2 + 2?",
        "answer": "4",
        "difficulty": "easy",
        "topic_id": 1,
        "prototype_id": 1,
    }

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.post("/tasks", json=payload)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_task(test_app):
    test_app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(role=UserRole.ADMIN)
    )

    payload = {
        "condition": "Сколько будет 2 + 2?",
        "answer": "4",
        "difficulty": "easy",
        "topic_id": 1,
        "prototype_id": 1,
    }

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.post("/tasks", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 2
    assert data["condition"] == payload["condition"]
    assert "answer" not in data