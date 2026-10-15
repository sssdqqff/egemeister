import pytest
from fastapi import HTTPException

from app.models.prototype import Prototype
from app.models.subject import Subject
from app.models.task import Task, TaskDifficulty
from app.models.topic import Topic
from app.schemas.prototype import PrototypeCreate, PrototypeUpdate
from app.services.prototype_service import PrototypeService


async def create_prototype(
    db_session,
    name="Test prototype",
    code="test-prototype",
    exam_number=15,
):
    return await PrototypeService(db_session).create_prototype(
        PrototypeCreate(
            name=name,
            code=code,
            description="Prototype integration test",
            exam_number=exam_number,
        )
    )


async def create_topic_context(db_session):
    subject = Subject(
        name="Prototype test subject",
        slug="prototype-test-subject",
        description="Subject for prototype integration tests",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name="Prototype test topic",
        slug="prototype-test-topic",
        subject_id=subject.id,
    )
    db_session.add(topic)
    await db_session.flush()

    return topic


@pytest.mark.asyncio
async def test_create_prototype_persists_in_database(db_session):
    result = await create_prototype(db_session)

    assert result.id is not None
    assert result.name == "Test prototype"
    assert result.code == "test-prototype"
    assert result.exam_number == 15
    assert result.is_active is True

    stored = await db_session.get(Prototype, result.id)
    assert stored is not None
    assert stored.code == result.code


@pytest.mark.asyncio
async def test_create_prototype_rejects_duplicate_code(db_session):
    await create_prototype(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await create_prototype(
            db_session,
            name="Another prototype",
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Prototype with this code already exists"


@pytest.mark.asyncio
async def test_get_missing_prototype_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await PrototypeService(db_session).get_prototype_by_id(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Prototype not found"


@pytest.mark.asyncio
async def test_update_prototype_persists_changes(db_session):
    created = await create_prototype(db_session)

    updated = await PrototypeService(db_session).update_prototype(
        created.id,
        PrototypeUpdate(
            name="Updated prototype",
            code="updated-prototype",
            exam_number=16,
        ),
    )

    assert updated.name == "Updated prototype"
    assert updated.code == "updated-prototype"
    assert updated.exam_number == 16

    stored = await db_session.get(Prototype, created.id)
    assert stored is not None
    assert stored.code == "updated-prototype"


@pytest.mark.asyncio
async def test_update_prototype_rejects_duplicate_code(db_session):
    first = await create_prototype(db_session)
    await create_prototype(
        db_session,
        name="Second prototype",
        code="second-prototype",
    )

    with pytest.raises(HTTPException) as exc_info:
        await PrototypeService(db_session).update_prototype(
            first.id,
            PrototypeUpdate(code="second-prototype"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Prototype with this code already exists"


@pytest.mark.asyncio
async def test_get_prototypes_filters_by_exam_number(db_session):
    first = await create_prototype(db_session)

    second = await create_prototype(
        db_session,
        name="Prototype for task 16",
        code="prototype-task-16",
        exam_number=16,
    )

    prototypes = await PrototypeService(db_session).get_all_prototypes(
        exam_number=15,
    )

    assert {prototype.id for prototype in prototypes} == {first.id}
    assert second.id not in {prototype.id for prototype in prototypes}


@pytest.mark.asyncio
async def test_prototype_can_be_deactivated_and_activated(db_session):
    created = await create_prototype(db_session)
    service = PrototypeService(db_session)

    await service.deactivate_prototype(created.id)

    deactivated = await service.get_prototype_by_id(created.id)
    assert deactivated.is_active is False

    await service.activate_prototype(created.id)

    activated = await service.get_prototype_by_id(created.id)
    assert activated.is_active is True


@pytest.mark.asyncio
async def test_permanent_delete_rejected_when_prototype_has_tasks(db_session):
    topic = await create_topic_context(db_session)
    prototype = await create_prototype(db_session)

    task = Task(
        condition="Calculate the value of 2 + 2.",
        answer="4",
        difficulty=TaskDifficulty.EASY,
        topic_id=topic.id,
        prototype_id=prototype.id,
    )
    db_session.add(task)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await PrototypeService(db_session).delete_prototype_permanently(
            prototype.id,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "Prototype has tasks and cannot be deleted"
    )

    stored_prototype = await db_session.get(Prototype, prototype.id)
    stored_task = await db_session.get(Task, task.id)

    assert stored_prototype is not None
    assert stored_task is not None


@pytest.mark.asyncio
async def test_permanent_delete_removes_prototype_without_tasks(db_session):
    created = await create_prototype(db_session)

    await PrototypeService(db_session).delete_prototype_permanently(
        created.id,
    )

    stored = await db_session.get(Prototype, created.id)
    assert stored is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation",
    [
        "deactivate_prototype",
        "activate_prototype",
        "delete_prototype_permanently",
    ],
)
async def test_prototype_operations_return_404_for_missing_prototype(
    db_session,
    operation,
):
    service = PrototypeService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await getattr(service, operation)(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Prototype not found"