from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.prototype import Prototype
from app.models.subject import Subject
from app.models.task import Task
from app.models.topic import Topic
from app.models.user import UserRole


@pytest_asyncio.fixture
async def api_client(db_session):
    original_overrides = app.dependency_overrides.copy()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest_asyncio.fixture
async def task_entities(db_session):
    subject = Subject(
        name="API test subject",
        slug="api-test-subject",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name="API test topic",
        slug="api-test-topic",
        subject_id=subject.id,
    )
    prototype = Prototype(
        name="API test prototype",
        code="api-test-prototype",
        exam_number=15,
    )

    db_session.add_all([topic, prototype])
    await db_session.flush()

    return topic, prototype


@pytest.mark.asyncio
async def test_admin_creates_task_through_api(
    api_client,
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(role=UserRole.ADMIN)
    )

    payload = {
        "condition": "Вычислите значение 2 + 2.",
        "answer": "4",
        "difficulty": "easy",
        "topic_id": topic.id,
        "prototype_id": prototype.id,
    }

    response = await api_client.post("/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["condition"] == payload["condition"]
    assert "answer" not in data

    stored_task = await db_session.scalar(
        select(Task).where(Task.id == data["id"])
    )
    assert stored_task is not None
    assert stored_task.answer == "4"

    get_response = await api_client.get("/tasks")

    assert get_response.status_code == 200
    tasks = get_response.json()
    created_task = next(
        task for task in tasks if task["id"] == data["id"]
    )
    assert "answer" not in created_task


@pytest.mark.asyncio
async def test_regular_user_cannot_create_task(
    api_client,
    task_entities,
):
    topic, prototype = task_entities
    app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(role="user")
    )

    response = await api_client.post(
        "/tasks",
        json={
            "condition": "Вычислите значение 2 + 2.",
            "answer": "4",
            "difficulty": "easy",
            "topic_id": topic.id,
            "prototype_id": prototype.id,
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tasks_requires_authentication(api_client):
    app.dependency_overrides.pop(get_current_user, None)

    response = await api_client.get("/tasks")

    assert response.status_code == 401