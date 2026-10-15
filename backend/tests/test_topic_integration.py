import pytest
from fastapi import HTTPException

from app.models.prototype import Prototype
from app.models.subject import Subject
from app.models.task import Task
from app.models.topic import Topic
from app.schemas.task import TaskCreate
from app.schemas.topic import TopicCreate, TopicUpdate
from app.services.task_service import TaskService
from app.services.topic_service import TopicService


async def create_subject(db_session):
    subject = Subject(
        name="Topic integration subject",
        slug="topic-integration-subject",
        description="Subject for topic integration tests",
    )
    db_session.add(subject)
    await db_session.flush()
    return subject


async def create_topic(
    db_session,
    subject_id,
    number=15,
    name="Logical expressions",
    slug="logical-expressions",
):
    return await TopicService(db_session).create_topic(
        TopicCreate(
            number=number,
            name=name,
            slug=slug,
            description="Topic integration test description",
            subject_id=subject_id,
        )
    )


@pytest.mark.asyncio
async def test_create_topic_persists_in_database(db_session):
    subject = await create_subject(db_session)

    result = await create_topic(db_session, subject.id)

    assert result.id is not None
    assert result.number == 15
    assert result.name == "Logical expressions"
    assert result.subject_id == subject.id
    assert result.is_active is True

    stored = await db_session.get(Topic, result.id)
    assert stored is not None
    assert stored.slug == "logical-expressions"


@pytest.mark.asyncio
async def test_create_topic_with_missing_subject_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await create_topic(db_session, subject_id=999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Subject not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("number", "slug", "expected_detail"),
    [
        (
            15,
            "another-topic",
            "Topic with this number already exists in the subject",
        ),
        (
            16,
            "logical-expressions",
            "Topic with this slug already exists in the subject",
        ),
    ],
)
async def test_create_topic_rejects_duplicates(
    db_session,
    number,
    slug,
    expected_detail,
):
    subject = await create_subject(db_session)
    await create_topic(db_session, subject.id)

    with pytest.raises(HTTPException) as exc_info:
        await create_topic(
            db_session,
            subject.id,
            number=number,
            name="Another topic",
            slug=slug,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == expected_detail


@pytest.mark.asyncio
async def test_get_missing_topic_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await TopicService(db_session).get_topic_by_id(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Topic not found"


@pytest.mark.asyncio
async def test_update_topic_persists_changes(db_session):
    subject = await create_subject(db_session)
    created = await create_topic(db_session, subject.id)

    updated = await TopicService(db_session).update_topic(
        created.id,
        TopicUpdate(
            name="Updated logical expressions",
            number=16,
            slug="updated-logical-expressions",
        ),
    )

    assert updated.name == "Updated logical expressions"
    assert updated.number == 16
    assert updated.slug == "updated-logical-expressions"

    stored = await db_session.get(Topic, created.id)
    assert stored is not None
    assert stored.number == 16


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("changes", "expected_detail"),
    [
        (
            {"number": 16},
            "Topic with this number already exists in the subject",
        ),
        (
            {"slug": "second-topic"},
            "Topic with this slug already exists in the subject",
        ),
    ],
)
async def test_update_topic_rejects_duplicates(
    db_session,
    changes,
    expected_detail,
):
    subject = await create_subject(db_session)
    first = await create_topic(
        db_session,
        subject.id,
        number=15,
        slug="first-topic",
    )
    await create_topic(
        db_session,
        subject.id,
        number=16,
        name="Second topic",
        slug="second-topic",
    )

    with pytest.raises(HTTPException) as exc_info:
        await TopicService(db_session).update_topic(
            first.id,
            TopicUpdate(**changes),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == expected_detail


@pytest.mark.asyncio
async def test_deactivated_topic_is_hidden_and_can_be_activated(db_session):
    subject = await create_subject(db_session)
    created = await create_topic(db_session, subject.id)
    service = TopicService(db_session)

    await service.deactivate_topic(created.id)

    active_topics = await service.get_all_topics()
    all_topics = await service.get_all_topics(only_active=False)

    assert created.id not in {topic.id for topic in active_topics}
    assert created.id in {topic.id for topic in all_topics}

    await service.activate_topic(created.id)

    active_topics = await service.get_all_topics()
    assert created.id in {topic.id for topic in active_topics}


@pytest.mark.asyncio
async def test_get_topics_filters_by_subject(db_session):
    first_subject = await create_subject(db_session)
    second_subject = Subject(
        name="Second topic integration subject",
        slug="second-topic-integration-subject",
        description="Second subject for integration tests",
    )
    db_session.add(second_subject)
    await db_session.flush()

    first_topic = await create_topic(db_session, first_subject.id)
    second_topic = await create_topic(
        db_session,
        second_subject.id,
        name="Another subject topic",
        slug="another-subject-topic",
    )

    topics = await TopicService(db_session).get_all_topics(
        subject_id=first_subject.id,
    )

    assert {topic.id for topic in topics} == {first_topic.id}
    assert second_topic.id not in {topic.id for topic in topics}


@pytest.mark.asyncio
async def test_permanent_delete_rejected_when_topic_has_tasks(db_session):
    subject = await create_subject(db_session)
    topic = await create_topic(db_session, subject.id)

    prototype = Prototype(
        name="Topic deletion prototype",
        code="topic-deletion-prototype",
        exam_number=topic.number,
    )
    db_session.add(prototype)
    await db_session.flush()

    task = await TaskService(db_session).create_task(
        TaskCreate(
            condition="Calculate the value of 2 + 2.",
            answer="4",
            difficulty="easy",
            topic_id=topic.id,
            prototype_id=prototype.id,
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await TopicService(db_session).delete_topic_permanently(topic.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "Cannot permanently delete topic with existing tasks"
    )

    stored = await db_session.get(Topic, topic.id)
    assert stored is not None

    stored_task = await db_session.get(Task, task.id)
    assert stored_task is not None


@pytest.mark.asyncio
async def test_permanent_delete_removes_topic_without_tasks(db_session):
    subject = await create_subject(db_session)
    topic = await create_topic(db_session, subject.id)

    await TopicService(db_session).delete_topic_permanently(topic.id)

    stored = await db_session.get(Topic, topic.id)
    assert stored is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation",
    [
        "deactivate_topic",
        "activate_topic",
        "delete_topic_permanently",
    ],
)
async def test_topic_operations_return_404_for_missing_topic(
    db_session,
    operation,
):
    service = TopicService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await getattr(service, operation)(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Topic not found"