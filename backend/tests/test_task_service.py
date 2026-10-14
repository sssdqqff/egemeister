from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


@pytest.fixture
def task_service():
    with (
        patch("app.services.task_service.TaskRepository") as task_repo_cls,
        patch("app.services.task_service.TopicRepository") as topic_repo_cls,
        patch("app.services.task_service.PrototypeRepository") as prototype_repo_cls,
    ):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()

        service = TaskService(db)

        yield (
            service,
            db,
            task_repo_cls.return_value,
            topic_repo_cls.return_value,
            prototype_repo_cls.return_value,
        )


@pytest.mark.asyncio
async def test_create_task_fails_if_topic_not_found(task_service):
    service, db, task_repo, topic_repo, prototype_repo = task_service

    topic_repo.get_by_id = AsyncMock(return_value=None)
    task_repo.create_task = AsyncMock()

    data = TaskCreate(
        condition="Сколько будет 2 + 2?",
        answer="4",
        difficulty="easy",
        topic_id=999,
        prototype_id=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_task(data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Topic not found"
    task_repo.create_task.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_fails_if_prototype_belongs_to_another_topic(task_service):
    service, db, task_repo, topic_repo, prototype_repo = task_service

    topic_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(number=15)
    )
    prototype_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(exam_number=14)
    )
    task_repo.create_task = AsyncMock()

    data = TaskCreate(
        condition="Сколько будет 2 + 2?",
        answer="4",
        difficulty="easy",
        topic_id=1,
        prototype_id=2,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_task(data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Prototype does not belong to this topic"
    task_repo.create_task.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_success(task_service):
    service, db, task_repo, topic_repo, prototype_repo = task_service

    topic_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(number=15)
    )
    prototype_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(exam_number=15)
    )

    data = TaskCreate(
        condition="Сколько будет 2 + 2?",
        answer="4",
        difficulty="easy",
        topic_id=1,
        prototype_id=2,
    )

    task_repo.create_task = AsyncMock(
        return_value=SimpleNamespace(
            id=10,
            condition=data.condition,
            answer=data.answer,
            difficulty=data.difficulty,
            is_active=True,
            topic_id=data.topic_id,
            prototype_id=data.prototype_id,
        )
    )

    result = await service.create_task(data)

    assert result.id == 10
    assert result.condition == data.condition
    assert result.difficulty == "easy"
    assert not hasattr(result, "answer")
    task_repo.create_task.assert_awaited_once_with(data)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_permanent_delete_fails_if_task_has_attempts(task_service):
    service, db, task_repo, topic_repo, prototype_repo = task_service

    task_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(id=10)
    )
    task_repo.has_attempts = AsyncMock(return_value=True)
    task_repo.delete_task_permanently = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_task_permanently(10)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "Cannot permanently delete task with existing attempts"
    )
    task_repo.delete_task_permanently.assert_not_awaited()
    db.commit.assert_not_awaited()