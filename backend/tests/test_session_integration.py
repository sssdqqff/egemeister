from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models.attempt import Attempt
from app.models.prototype import Prototype
from app.models.session import Session as TrainingSession
from app.models.session import SessionStatus, SessionType
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.user import User
from app.schemas.session import SessionCreate
from app.schemas.task import TaskCreate
from app.services.session_service import SessionService
from app.services.task_service import TaskService


async def create_test_user(db_session, first_name="Test user"):
    user = User(first_name=first_name)
    db_session.add(user)
    await db_session.flush()
    return user


async def create_task_context(db_session, suffix="test"):
    subject = Subject(
        name=f"Session test subject {suffix}",
        slug=f"session-test-subject-{suffix}",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name=f"Session test topic {suffix}",
        slug=f"session-test-topic-{suffix}",
        subject_id=subject.id,
    )
    prototype = Prototype(
        name=f"Session test prototype {suffix}",
        code=f"session-test-prototype-{suffix}",
        exam_number=15,
    )

    db_session.add_all([topic, prototype])
    await db_session.flush()

    return topic, prototype


async def create_test_task(db_session, topic, prototype, condition, answer):
    service = TaskService(db_session)
    return await service.create_task(
        TaskCreate(
            condition=condition,
            answer=answer,
            difficulty="easy",
            topic_id=topic.id,
            prototype_id=prototype.id,
        )
    )


@pytest.mark.asyncio
async def test_create_session_persists_in_database(db_session):
    user = await create_test_user(db_session)
    service = SessionService(db_session)

    result = await service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )

    stored = await db_session.get(TrainingSession, result.id)

    assert stored is not None
    assert stored.user_id == user.id
    assert result.type == "practice"
    assert result.status == "in_progress"
    assert stored.finished_at is None


@pytest.mark.asyncio
async def test_duplicate_active_session_of_same_type_returns_409(db_session):
    user = await create_test_user(db_session)
    service = SessionService(db_session)

    await service.create_session(user.id, SessionCreate(type="practice"))

    with pytest.raises(HTTPException) as exc_info:
        await service.create_session(user.id, SessionCreate(type="practice"))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "You already have an active session of this type"


@pytest.mark.asyncio
async def test_different_session_types_can_be_active(db_session):
    user = await create_test_user(db_session)
    service = SessionService(db_session)

    practice = await service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )
    exam = await service.create_session(
        user.id,
        SessionCreate(type="exam"),
    )

    assert practice.status == "in_progress"
    assert exam.status == "in_progress"
    assert practice.id != exam.id


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_session(db_session):
    owner = await create_test_user(db_session, "Session owner")
    other_user = await create_test_user(db_session, "Other user")
    service = SessionService(db_session)

    created = await service.create_session(
        owner.id,
        SessionCreate(type="practice"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_session_by_id(created.id, other_user.id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


@pytest.mark.asyncio
async def test_finish_session_sets_status_and_finish_time(db_session):
    user = await create_test_user(db_session)
    service = SessionService(db_session)

    created = await service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )

    result = await service.finish_session(created.id, user.id)

    assert result.status == "completed"
    assert result.finished_at is not None

    with pytest.raises(HTTPException) as exc_info:
        await service.finish_session(created.id, user.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Session is already finished"


@pytest.mark.asyncio
async def test_session_tasks_exclude_tasks_already_answered(db_session):
    user = await create_test_user(db_session)
    topic, prototype = await create_task_context(db_session, "answered")

    session_service = SessionService(db_session)
    created_session = await session_service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )

    answered_task = await create_test_task(
        db_session,
        topic,
        prototype,
        "Вычислите значение 2 + 2.",
        "4",
    )
    unanswered_task = await create_test_task(
        db_session,
        topic,
        prototype,
        "Вычислите значение 3 + 3.",
        "6",
    )

    db_session.add(
        Attempt(
            user_id=user.id,
            task_id=answered_task.id,
            session_id=created_session.id,
            user_answer="4",
            is_correct=True,
        )
    )
    await db_session.flush()

    tasks = await session_service.get_session_tasks(
        session_id=created_session.id,
        user_id=user.id,
        topic_id=topic.id,
        count=10,
    )

    returned_ids = {task.id for task in tasks}

    assert answered_task.id not in returned_ids
    assert returned_ids == {unanswered_task.id}
    assert all(not hasattr(task, "answer") for task in tasks)


@pytest.mark.asyncio
async def test_finished_session_cannot_provide_tasks(db_session):
    user = await create_test_user(db_session)
    service = SessionService(db_session)

    created = await service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )
    await service.finish_session(created.id, user.id)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_session_tasks(
            session_id=created.id,
            user_id=user.id,
            topic_id=1,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Session is already finished"


@pytest.mark.asyncio
async def test_session_summary_calculates_accuracy(db_session):
    user = await create_test_user(db_session)
    topic, prototype = await create_task_context(db_session, "summary")
    service = SessionService(db_session)

    created = await service.create_session(
        user.id,
        SessionCreate(type="practice"),
    )
    task = await create_test_task(
        db_session,
        topic,
        prototype,
        "Вычислите значение 2 + 2.",
        "4",
    )

    db_session.add_all([
        Attempt(
            user_id=user.id,
            task_id=task.id,
            session_id=created.id,
            user_answer="4",
            is_correct=True,
        ),
        Attempt(
            user_id=user.id,
            task_id=task.id,
            session_id=created.id,
            user_answer="5",
            is_correct=False,
        ),
    ])
    await db_session.flush()

    summary = await service.get_session_summary(created.id, user.id)

    assert summary.session_id == created.id
    assert summary.status == "in_progress"
    assert summary.total_attempts == 2
    assert summary.correct_attempts == 1
    assert summary.accuracy == 50.0
    assert summary.duration_seconds >= 0


@pytest.mark.asyncio
async def test_expired_session_is_completed_when_accessed(db_session):
    user = await create_test_user(db_session)

    expired_session = TrainingSession(
        user_id=user.id,
        session_type=SessionType.PRACTICE,
        status=SessionStatus.IN_PROGRESS,
        time_limit_seconds=1,
        created_at=datetime.now(timezone.utc) - timedelta(seconds=10),
    )
    db_session.add(expired_session)
    await db_session.flush()
    await db_session.refresh(expired_session)

    service = SessionService(db_session)
    result = await service.get_session_by_id(expired_session.id, user.id)

    assert result.status == "completed"
    assert result.finished_at is not None