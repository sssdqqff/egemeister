import pytest
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.schemas.user import UserUpdate
from app.services.user_service import UserService


async def create_user(db_session, **kwargs):
    user = User(first_name="User service test", **kwargs)
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_get_user_by_id_returns_user(db_session):
    user = await create_user(db_session, username="test_user")

    result = await UserService(db_session).get_user_by_id(user.id)

    assert result.id == user.id
    assert result.username == "test_user"


@pytest.mark.asyncio
async def test_get_missing_user_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).get_user_by_id(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_all_users_filters_by_role_and_active_status(db_session):
    admin = await create_user(
        db_session,
        username="active_admin",
        role=UserRole.ADMIN,
    )
    inactive_admin = await create_user(
        db_session,
        username="inactive_admin",
        role=UserRole.ADMIN,
        is_active=False,
    )
    await create_user(db_session, username="regular_user")

    service = UserService(db_session)

    active_admins = await service.get_all_users(role=UserRole.ADMIN)
    all_admins = await service.get_all_users(
        role=UserRole.ADMIN,
        only_active=False,
    )

    assert {user.id for user in active_admins} == {admin.id}
    assert {user.id for user in all_admins} == {
        admin.id,
        inactive_admin.id,
    }


@pytest.mark.asyncio
async def test_update_user_persists_username_and_normalizes_email(db_session):
    user = await create_user(db_session)

    result = await UserService(db_session).update_user(
        user.id,
        UserUpdate(
            username="maxim",
            email="MAXIM@example.com",
        ),
    )

    assert result.username == "maxim"
    assert result.email == "maxim@example.com"

    await db_session.refresh(user)
    assert user.username == "maxim"
    assert user.email == "maxim@example.com"


@pytest.mark.asyncio
async def test_update_user_rejects_duplicate_username(db_session):
    first = await create_user(db_session, username="first_user")
    await create_user(db_session, username="second_user")

    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).update_user(
            first.id,
            UserUpdate(username="second_user"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Username already taken"


@pytest.mark.asyncio
async def test_update_user_rejects_duplicate_email(db_session):
    first = await create_user(db_session, email="first@example.com")
    await create_user(db_session, email="second@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).update_user(
            first.id,
            UserUpdate(email="second@example.com"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already registered"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"username": None},
        {"email": None},
    ],
)
async def test_update_user_rejects_explicit_null_fields(
    db_session,
    payload,
):
    user = await create_user(db_session, username="valid_user")

    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).update_user(
            user.id,
            UserUpdate(**payload),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Fields cannot be null"


@pytest.mark.asyncio
async def test_update_missing_user_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).update_user(
            999999,
            UserUpdate(username="new_username"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_user_can_keep_own_username(db_session):
    user = await create_user(db_session, username="same_username")

    result = await UserService(db_session).update_user(
        user.id,
        UserUpdate(username="same_username"),
    )

    assert result.username == "same_username"


@pytest.mark.asyncio
async def test_deactivate_user_persists_status(db_session):
    user = await create_user(db_session, username="to_deactivate")

    await UserService(db_session).deactivate_user(user.id)

    await db_session.refresh(user)
    assert user.is_active is False


@pytest.mark.asyncio
async def test_deactivate_missing_user_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await UserService(db_session).deactivate_user(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"