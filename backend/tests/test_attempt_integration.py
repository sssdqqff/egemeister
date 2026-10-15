from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models.attempt import Attempt
from app.models.prototype import Prototype
from app.models.session import Session as TrainingSession
from app.models.session import SessionDifficulty, SessionStatus, SessionType
from app.models.subject import Subject
from app.models.task import Task
from app.models.topic import Topic
from app.models.user import User
from app.schemas.attempt import AttemptCreate
from app.schemas.session import SessionCreate
from app.schemas.task import TaskCreate
from app.services.attempt_service import AttemptService, is_answer_correct
from app.services.session_service import SessionService
from app.services.task_service import TaskService


async def create_test_user(db_session, name="Attempt test user"):
    user = User(first_name=name)
    db_session.add(user)
    await db_session.flush()
    return user


async def create_test_task(db_session, suffix="test", answer="4"):
    subject = Subject(
        name=f"Attempt subject {suffix}",
        slug=f"attempt-subject-{suffix}",
    )
    db_session.add(subject)
    await db_session.flush()

    topic = Topic(
        number=15,
        name=f"Attempt topic {suffix}",
        slug=f"attempt-topic-{suffix}",
        subject_id=subject.id,
    )
    prototype = Prototype(
        name=f"Attempt prototype {suffix}",
        code=f"attempt-prototype-{suffix}",
        exam_number=15,
    )
    db_session.add_all([topic, prototype])
    await db_session.flush()

    return await TaskService(db_session).create_task(
        TaskCreate(
            condition="Вычислите значение 2 + 2.",
            answer=answer,
            difficulty="easy",
            topic_id=topic.id,
            prototype_id=prototype.id,
        )
    )


async def create_test_session(db_session, user_id):
    return await SessionService(db_session).create_session(
        user_id,
        SessionCreate(type="practice"),
    )


@pytest.mark.parametrize(
    ("correct", "given", "expected"),
    [
        ("  Ёж  ", "еж", True),
        ("4,00", "4.0", True),
        ("правильно", "неправильно", False),
    ],
)
def test_is_answer_correct_normalizes_answers(correct, given, expected):
    assert is_answer_correct(correct, given) is expected


@pytest.mark.asyncio
async def test_submit_correct_attempt_persists_in_database(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session, answer="4,00")

    result = await AttemptService(db_session).submit_attempt(
        user.id,
        AttemptCreate(task_id=task.id, user_answer="4.0"),
    )

    assert result.is_correct is True

    stored = await db_session.get(Attempt, result.id)
    assert stored is not None
    assert stored.user_id == user.id
    assert stored.task_id == task.id
    assert stored.user_answer == "4.0"
    assert stored.is_correct is True


@pytest.mark.asyncio
async def test_submit_incorrect_attempt_is_recorded_as_incorrect(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session)

    result = await AttemptService(db_session).submit_attempt(
        user.id,
        AttemptCreate(task_id=task.id, user_answer="5"),
    )

    assert result.is_correct is False

    stored = await db_session.get(Attempt, result.id)
    assert stored is not None
    assert stored.user_answer == "5"
    assert stored.is_correct is False


@pytest.mark.asyncio
async def test_submit_attempt_for_missing_task_returns_404(db_session):
    user = await create_test_user(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).submit_attempt(
            user.id,
            AttemptCreate(task_id=999999, user_answer="4"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_submit_attempt_for_inactive_task_returns_404(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session)

    stored_task = await db_session.get(Task, task.id)
    stored_task.is_active = False
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).submit_attempt(
            user.id,
            AttemptCreate(task_id=task.id, user_answer="4"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_duplicate_attempt_in_session_returns_409(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session)
    session = await create_test_session(db_session, user.id)
    service = AttemptService(db_session)

    await service.submit_attempt(
        user.id,
        AttemptCreate(
            task_id=task.id,
            session_id=session.id,
            user_answer="4",
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.submit_attempt(
            user.id,
            AttemptCreate(
                task_id=task.id,
                session_id=session.id,
                user_answer="5",
            ),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Task already answered in this session"


@pytest.mark.asyncio
async def test_attempt_cannot_use_another_users_session(db_session):
    owner = await create_test_user(db_session, "Session owner")
    another_user = await create_test_user(db_session, "Another user")
    task = await create_test_task(db_session)
    session = await create_test_session(db_session, owner.id)

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).submit_attempt(
            another_user.id,
            AttemptCreate(
                task_id=task.id,
                session_id=session.id,
                user_answer="4",
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


@pytest.mark.asyncio
async def test_attempt_in_finished_session_returns_409(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session)
    session = await create_test_session(db_session, user.id)

    await SessionService(db_session).finish_session(session.id, user.id)

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).submit_attempt(
            user.id,
            AttemptCreate(
                task_id=task.id,
                session_id=session.id,
                user_answer="4",
            ),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Session is already finished"


@pytest.mark.asyncio
async def test_expired_session_is_closed_and_attempt_rejected(db_session):
    user = await create_test_user(db_session)
    task = await create_test_task(db_session)

    session = TrainingSession(
        user_id=user.id,
        session_type=SessionType.PRACTICE,
        status=SessionStatus.IN_PROGRESS,
        difficulty=SessionDifficulty.EASY,
        time_limit_seconds=1,
        created_at=datetime.now(timezone.utc) - timedelta(seconds=10),
    )
    db_session.add(session)
    await db_session.flush()
    await db_session.refresh(session)

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).submit_attempt(
            user.id,
            AttemptCreate(
                task_id=task.id,
                session_id=session.id,
                user_answer="4",
            ),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Session time limit exceeded"

    await db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED
    assert session.finished_at is not None


@pytest.mark.asyncio
async def test_user_cannot_read_another_users_attempt(db_session):
    owner = await create_test_user(db_session, "Attempt owner")
    another_user = await create_test_user(db_session, "Another user")
    task = await create_test_task(db_session)

    attempt = await AttemptService(db_session).submit_attempt(
        owner.id,
        AttemptCreate(task_id=task.id, user_answer="4"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await AttemptService(db_session).get_attempt_by_id(
            attempt.id,
            another_user.id,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Attempt not found"