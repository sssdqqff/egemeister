from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.attempt import Attempt
from app.models.prototype import Prototype
from app.models.subject import Subject
from app.models.task import Task
from app.models.topic import Topic
from app.models.user import User
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


async def create_user(db_session, name="Attempt API user"):
    user = User(first_name=name)
    db_session.add(user)
    await db_session.flush()
    return user


async def create_task(db_session):
    subject = Subject(
        name="Attempt API subject",
        slug="attempt-api-subject",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name="Attempt API topic",
        slug="attempt-api-topic",
        subject_id=subject.id,
    )
    prototype = Prototype(
        name="Attempt API prototype",
        code="attempt-api-prototype",
        exam_number=15,
    )
    db_session.add_all([topic, prototype])
    await db_session.flush()

    return await TaskService(db_session).create_task(
        TaskCreate(
            condition="Вычислите значение 2 + 2.",
            answer="4",
            difficulty="easy",
            topic_id=topic.id,
            prototype_id=prototype.id,
        )
    )


@pytest_asyncio.fixture
async def attempt_api_client(db_session):
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
async def test_submit_correct_attempt_through_api(
    db_session,
    attempt_api_client,
):
    client, current_user = attempt_api_client
    user = await create_user(db_session)
    task = await create_task(db_session)
    current_user.id = user.id

    response = await client.post(
        "/attempts",
        json={
            "task_id": task.id,
            "user_answer": "4.0",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["is_correct"] is True
    assert data["task_id"] == task.id
    assert data["user_answer"] == "4.0"
    assert "answer" not in data

    stored = await db_session.scalar(
        select(Attempt).where(Attempt.id == data["id"])
    )
    assert stored is not None
    assert stored.user_id == user.id
    assert stored.is_correct is True


@pytest.mark.asyncio
async def test_submit_incorrect_attempt_through_api(
    db_session,
    attempt_api_client,
):
    client, current_user = attempt_api_client
    user = await create_user(db_session)
    task = await create_task(db_session)
    current_user.id = user.id

    response = await client.post(
        "/attempts",
        json={
            "task_id": task.id,
            "user_answer": "5",
        },
    )

    assert response.status_code == 201
    assert response.json()["is_correct"] is False


@pytest.mark.asyncio
async def test_user_cannot_read_another_users_attempt(
    db_session,
    attempt_api_client,
):
    client, current_user = attempt_api_client
    owner = await create_user(db_session, "Attempt owner")
    another_user = await create_user(db_session, "Another user")
    task = await create_task(db_session)
    current_user.id = owner.id

    created = await client.post(
        "/attempts",
        json={
            "task_id": task.id,
            "user_answer": "4",
        },
    )
    assert created.status_code == 201

    current_user.id = another_user.id
    response = await client.get(
        f"/attempts/{created.json()['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attempt not found"


@pytest.mark.asyncio
async def test_attempts_endpoint_requires_authentication(
    attempt_api_client,
):
    client, _ = attempt_api_client
    app.dependency_overrides.pop(get_current_user, None)

    response = await client.get("/attempts")

    assert response.status_code == 401