import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import select

from app.models.prototype import Prototype
from app.models.subject import Subject
from app.models.task import Task
from app.models.topic import Topic
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService

@pytest_asyncio.fixture
async def task_entities(db_session):
    subject = Subject(
        name="Test informatics",
        slug="test-informatics",
        description="Test subject",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name="Test topic",
        slug="test-topic-15",
        subject_id=subject.id,
    )
    prototype = Prototype(
        name="Test segments",
        code="test-segments-15",
        exam_number=15,
    )

    db_session.add_all([topic, prototype])
    await db_session.flush()

    return topic, prototype


@pytest.mark.asyncio
async def test_create_task_persists_in_database(db_session, task_entities):
    topic, prototype = task_entities
    service = TaskService(db_session)

    data = TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    )

    result = await service.create_task(data)

    assert result.id is not None
    assert result.condition == data.condition
    assert not hasattr(result, "answer")

    stored_task = await db_session.scalar(
        select(Task).where(Task.id == result.id)
    )

    assert stored_task is not None
    assert stored_task.answer == "4"
    assert stored_task.topic_id == topic.id
    assert stored_task.prototype_id == prototype.id


@pytest.mark.asyncio
async def test_create_task_fails_for_missing_topic(db_session, task_entities):
    topic, prototype = task_entities
    service = TaskService(db_session)

    data = TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=999999,
        prototype_id=prototype.id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_task(data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Topic not found"


@pytest.mark.asyncio
async def test_create_task_fails_for_mismatched_prototype(
    db_session,
    task_entities,
):
    topic, _ = task_entities

    wrong_prototype = Prototype(
        name="Test wrong prototype",
        code="test-prototype-14",
        exam_number=14,
    )
    db_session.add(wrong_prototype)
    await db_session.flush()

    service = TaskService(db_session)

    data = TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=wrong_prototype.id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_task(data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Prototype does not belong to this topic"


@pytest.mark.asyncio
async def test_task_can_be_deactivated_and_activated(
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    service = TaskService(db_session)

    data = TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    )

    task = await service.create_task(data)

    await service.deactivate_task(task.id)

    stored_task = await db_session.scalar(
        select(Task).where(Task.id == task.id)
    )
    assert stored_task is not None
    assert stored_task.is_active is False

    await service.activate_task(task.id)

    stored_task = await db_session.scalar(
        select(Task).where(Task.id == task.id)
    )
    assert stored_task is not None
    assert stored_task.is_active is True


@pytest.mark.asyncio
async def test_update_task_persists_changes(db_session, task_entities):
    topic, prototype = task_entities
    service = TaskService(db_session)

    task = await service.create_task(TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    updated = await service.update_task(
        task.id,
        TaskUpdate(condition="Вычислите значение 10 + 5."),
    )

    assert updated.condition == "Вычислите значение 10 + 5."

    stored_task = await db_session.scalar(
        select(Task).where(Task.id == task.id)
    )

    assert stored_task.condition == "Вычислите значение 10 + 5."
    assert stored_task.answer == "4"


@pytest.mark.asyncio
async def test_get_missing_task_returns_404(db_session):
    service = TaskService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_task_by_id(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_permanent_delete_removes_task_from_database(
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    service = TaskService(db_session)

    task = await service.create_task(TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    task_id = task.id

    await service.delete_task_permanently(task_id)

    deleted_task = await db_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert deleted_task is None


@pytest.mark.asyncio
async def test_get_all_tasks_filters_by_difficulty(
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    service = TaskService(db_session)

    easy_task = await service.create_task(TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    await service.create_task(TaskCreate(
        condition="Вычислите остаток от деления 17 на 5.",
        answer="2",
        difficulty="medium",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    tasks = await service.get_all_tasks(
        topic_id=topic.id,
        prototype_id=prototype.id,
        difficulty="easy",
    )

    assert len(tasks) == 1
    assert tasks[0].id == easy_task.id


@pytest.mark.asyncio
async def test_get_all_tasks_excludes_inactive_by_default(
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    service = TaskService(db_session)

    active_task = await service.create_task(TaskCreate(
        condition="Вычислите значение 2 + 2.",
        answer="4",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    inactive_task = await service.create_task(TaskCreate(
        condition="Вычислите значение 3 + 3.",
        answer="6",
        difficulty="easy",
        topic_id=topic.id,
        prototype_id=prototype.id,
    ))

    await service.deactivate_task(inactive_task.id)

    active_tasks = await service.get_all_tasks(topic_id=topic.id)
    all_tasks = await service.get_all_tasks(
        topic_id=topic.id,
        only_active=False,
    )

    assert [task.id for task in active_tasks] == [active_task.id]
    assert {task.id for task in all_tasks} == {
        active_task.id,
        inactive_task.id,
    }


@pytest.mark.asyncio
async def test_get_random_tasks_excludes_previous_tasks(
    db_session,
    task_entities,
):
    topic, prototype = task_entities
    service = TaskService(db_session)

    created_tasks = []

    for index in range(3):
        task = await service.create_task(TaskCreate(
            condition=f"Вычислите значение {index + 2} + 2.",
            answer=str(index + 4),
            difficulty="easy",
            topic_id=topic.id,
            prototype_id=prototype.id,
        ))
        created_tasks.append(task)

    excluded_task = created_tasks[0]
    expected_ids = {task.id for task in created_tasks[1:]}

    tasks = await service.get_random_tasks(
        topic_id=topic.id,
        count=10,
        exclude_ids=[excluded_task.id],
    )

    returned_ids = {task.id for task in tasks}

    assert excluded_task.id not in returned_ids
    assert returned_ids == expected_ids


@pytest.mark.asyncio
async def test_update_missing_task_returns_404(db_session):
    service = TaskService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.update_task(
            999999,
            TaskUpdate(condition="Обновлённое условие задачи"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_deactivate_missing_task_returns_404(db_session):
    service = TaskService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.deactivate_task(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_activate_missing_task_returns_404(db_session):
    service = TaskService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.activate_task(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_permanent_delete_missing_task_returns_404(db_session):
    service = TaskService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_task_permanently(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"