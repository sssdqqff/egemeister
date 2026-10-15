import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.subject import Subject
from app.models.topic import Topic
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.services.subject_service import SubjectService


async def create_test_subject(db_session, name="Test Informatics", slug="test-informatics"):
    return await SubjectService(db_session).create_subject(
        SubjectCreate(
            name=name,
            slug=slug,
            description="Test subject description",
        )
    )


@pytest.mark.asyncio
async def test_create_subject_persists_in_database(db_session):
    service = SubjectService(db_session)

    result = await service.create_subject(
        SubjectCreate(
            name="Test Informatics",
            slug="test-informatics",
            description="Test subject description",
        )
    )

    assert result.id is not None
    assert result.name == "Test Informatics"
    assert result.slug == "test-informatics"
    assert result.is_active is True

    stored = await db_session.get(Subject, result.id)
    assert stored is not None
    assert stored.name == result.name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "slug", "expected_detail"),
    [
        (
            "Test Informatics",
            "another-informatics",
            "Subject with this name already exists",
        ),
        (
            "Another Subject",
            "test-informatics",
            "Subject with this slug already exists",
        ),
    ],
)
async def test_create_subject_rejects_duplicates(
    db_session,
    name,
    slug,
    expected_detail,
):
    await create_test_subject(db_session)
    service = SubjectService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_subject(
            SubjectCreate(
                name=name,
                slug=slug,
                description="Another test description",
            )
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == expected_detail


@pytest.mark.asyncio
async def test_get_missing_subject_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await SubjectService(db_session).get_subject_by_id(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Subject not found"


@pytest.mark.asyncio
async def test_update_subject_persists_changes(db_session):
    created = await create_test_subject(db_session)
    service = SubjectService(db_session)

    updated = await service.update_subject(
        created.id,
        SubjectUpdate(
            name="Updated Informatics",
            description="Updated subject description",
        ),
    )

    assert updated.name == "Updated Informatics"
    assert updated.description == "Updated subject description"
    assert updated.slug == "test-informatics"

    stored = await db_session.get(Subject, created.id)
    assert stored is not None
    assert stored.name == "Updated Informatics"


@pytest.mark.asyncio
async def test_update_subject_rejects_duplicate_name(db_session):
    first = await create_test_subject(db_session)
    await create_test_subject(
        db_session,
        name="Second Subject",
        slug="second-subject",
    )

    with pytest.raises(HTTPException) as exc_info:
        await SubjectService(db_session).update_subject(
            first.id,
            SubjectUpdate(name="Second Subject"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Subject with this name already exists"


@pytest.mark.asyncio
async def test_deactivated_subject_is_hidden_by_default(db_session):
    created = await create_test_subject(db_session)
    service = SubjectService(db_session)

    await service.deactivate_subject(created.id)

    active_subjects = await service.get_all_subjects()
    all_subjects = await service.get_all_subjects(only_active=False)

    assert created.id not in {subject.id for subject in active_subjects}
    assert created.id in {subject.id for subject in all_subjects}

    await service.activate_subject(created.id)

    active_subjects = await service.get_all_subjects()
    assert created.id in {subject.id for subject in active_subjects}


@pytest.mark.asyncio
async def test_permanent_delete_rejected_when_subject_has_topics(db_session):
    created = await create_test_subject(db_session)

    db_session.add(
        Topic(
            number=15,
            name="Test topic",
            slug="test-topic",
            subject_id=created.id,
        )
    )
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await SubjectService(db_session).delete_subject_permanently(created.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "Cannot permanently delete subject with existing topics"
    )

    stored = await db_session.get(Subject, created.id)
    assert stored is not None


@pytest.mark.asyncio
async def test_permanent_delete_removes_subject_without_topics(db_session):
    created = await create_test_subject(db_session)

    await SubjectService(db_session).delete_subject_permanently(created.id)

    stored = await db_session.get(Subject, created.id)
    assert stored is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation",
    [
        "deactivate_subject",
        "activate_subject",
        "delete_subject_permanently",
    ],
)
async def test_subject_operations_return_404_for_missing_subject(
    db_session,
    operation,
):
    service = SubjectService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await getattr(service, operation)(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Subject not found"