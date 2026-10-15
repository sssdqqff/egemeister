from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models.profile import Profile
from app.models.user import User
from app.services.profile_service import (
    ProfileService,
    calculate_level,
    xp_for_level,
)


async def create_profile(
    db_session,
    xp=0,
    level=1,
    streak=0,
    last_login=None,
):
    user = User(first_name="Profile test user")
    db_session.add(user)
    await db_session.flush()

    profile = Profile(
        user_id=user.id,
        xp=xp,
        level=level,
        streak=streak,
        last_login=last_login,
    )
    db_session.add(profile)
    await db_session.flush()

    return user, profile


@pytest.mark.parametrize(
    ("xp", "expected_level"),
    [
        (0, 1),
        (99, 1),
        (100, 2),
        (299, 2),
        (300, 3),
        (599, 3),
        (600, 4),
    ],
)
def test_calculate_level_at_xp_boundaries(xp, expected_level):
    assert calculate_level(xp) == expected_level


def test_xp_for_level_uses_increasing_thresholds():
    assert xp_for_level(1) == 100
    assert xp_for_level(2) == 300
    assert xp_for_level(3) == 600


@pytest.mark.asyncio
async def test_add_xp_updates_level_and_persists(db_session):
    user, profile = await create_profile(
        db_session,
        xp=90,
        level=1,
    )

    result = await ProfileService(db_session).add_xp(user.id, 10)

    assert result.xp == 100
    assert result.level == 2

    await db_session.refresh(profile)
    assert profile.xp == 100
    assert profile.level == 2


@pytest.mark.asyncio
async def test_add_xp_rejects_negative_amount(db_session):
    user, profile = await create_profile(
        db_session,
        xp=50,
        level=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        await ProfileService(db_session).add_xp(user.id, -10)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "XP amount cannot be negative"

    await db_session.refresh(profile)
    assert profile.xp == 50
    assert profile.level == 1


@pytest.mark.asyncio
async def test_get_missing_profile_returns_404(db_session):
    user = User(first_name="User without profile")
    db_session.add(user)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await ProfileService(db_session).get_profile(user.id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_update_avatar_persists_url(db_session):
    user, profile = await create_profile(db_session)
    avatar_url = "https://example.com/avatar.png"

    result = await ProfileService(db_session).update_avatar(
        user.id,
        avatar_url,
    )

    assert str(result.avatar_url) == avatar_url

    await db_session.refresh(profile)
    assert profile.avatar_url == avatar_url


@pytest.mark.asyncio
async def test_record_login_creates_profile(db_session):
    user = User(first_name="New login user")
    db_session.add(user)
    await db_session.flush()

    result = await ProfileService(db_session).record_login(user.id)

    assert result.streak == 1
    assert result.last_login is not None

    profile = await db_session.get(Profile, result.id)
    assert profile is not None
    assert profile.user_id == user.id


@pytest.mark.parametrize(
    ("days_ago", "initial_streak", "expected_streak"),
    [
        (0, 5, 5),
        (1, 5, 6),
        (3, 5, 1),
    ],
)
@pytest.mark.asyncio
async def test_record_login_updates_streak(
    db_session,
    days_ago,
    initial_streak,
    expected_streak,
):
    last_login = datetime.now(timezone.utc) - timedelta(days=days_ago)

    user, _ = await create_profile(
        db_session,
        streak=initial_streak,
        last_login=last_login,
    )

    result = await ProfileService(db_session).record_login(user.id)

    assert result.streak == expected_streak
    assert result.last_login is not None