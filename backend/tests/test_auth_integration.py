from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.dependencies import get_db
from app.main import app
from app.models.auth_session import AuthSession
from app.models.login_code import LoginCode
from app.models.user import User, UserRole
from app.security import hash_login_code, hash_session_token
from app.rate_limit import login_limiter


@pytest.fixture(autouse=True)
def isolate_login_failures():
    login_limiter._failures.clear()
    yield
    login_limiter._failures.clear()


@pytest_asyncio.fixture
async def auth_client(db_session):
    original_overrides = app.dependency_overrides.copy()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="https://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


async def request_login_code(client, telegram_id=740000001):
    return await client.post(
        "/internal/bot/login-codes",
        headers={"X-Bot-Key": settings.bot_api_key},
        json={
            "telegram_id": telegram_id,
            "first_name": "Auth test user",
        },
    )


async def exchange_code(client, code):
    return await client.post(
        "/auth/telegram/exchange",
        json={"code": code},
    )


@pytest.mark.asyncio
async def test_bot_login_code_requires_valid_bot_key(auth_client):
    response = await auth_client.post(
        "/internal/bot/login-codes",
        headers={"X-Bot-Key": "invalid-key"},
        json={
            "telegram_id": 740000001,
            "first_name": "Auth test user",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_deactivated_user_cannot_request_login_code(
    db_session,
    auth_client,
):
    user = User(
        telegram_id=740000002,
        first_name="Deactivated user",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()

    response = await request_login_code(auth_client, user.telegram_id)

    assert response.status_code == 403
    assert response.json()["detail"] == "User is deactivated"


@pytest.mark.asyncio
async def test_exchange_code_sets_cookie_and_authenticates_user(auth_client):
    code_response = await request_login_code(auth_client)
    assert code_response.status_code == 200

    code = code_response.json()["code"]
    response = await exchange_code(auth_client, code)

    assert response.status_code == 200

    cookie = response.headers["set-cookie"]
    assert settings.session_cookie_name in cookie
    assert "httponly" in cookie.lower()
    assert f"samesite={settings.cookie_samesite}".lower() in cookie.lower()

    if settings.cookie_secure:
        assert "secure" in cookie.lower()

    user_data = response.json()
    me_response = await auth_client.get("/users/me")

    assert me_response.status_code == 200
    assert me_response.json()["id"] == user_data["id"]


@pytest.mark.asyncio
async def test_invalid_login_code_is_rejected(auth_client):
    response = await exchange_code(auth_client, "999999")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired code"


@pytest.mark.asyncio
async def test_expired_login_code_is_rejected(
    db_session,
    auth_client,
):
    code_response = await request_login_code(auth_client, 740000003)
    assert code_response.status_code == 200

    code = code_response.json()["code"]
    stored_code = await db_session.scalar(
        select(LoginCode).where(
            LoginCode.code_hash == hash_login_code(code)
        )
    )
    assert stored_code is not None

    stored_code.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.flush()

    response = await exchange_code(auth_client, code)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired code"


@pytest.mark.asyncio
async def test_login_code_can_only_be_used_once(auth_client):
    code_response = await request_login_code(auth_client, 740000004)
    assert code_response.status_code == 200

    code = code_response.json()["code"]

    first_response = await exchange_code(auth_client, code)
    assert first_response.status_code == 200

    second_response = await exchange_code(auth_client, code)

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Invalid or expired code"


@pytest.mark.asyncio
async def test_logout_revokes_current_session(
    db_session,
    auth_client,
):
    code_response = await request_login_code(auth_client, 740000005)
    assert code_response.status_code == 200

    response = await exchange_code(
        auth_client,
        code_response.json()["code"],
    )
    assert response.status_code == 200

    session = await db_session.scalar(
        select(AuthSession).where(
            AuthSession.user_id == response.json()["id"]
        )
    )
    assert session is not None

    me_response = await auth_client.get("/users/me")
    assert me_response.status_code == 200

    logout_response = await auth_client.post("/auth/logout")
    assert logout_response.status_code == 204

    await db_session.refresh(session)
    assert session.revoked_at is not None

    me_response = await auth_client.get("/users/me")
    assert me_response.status_code == 401


@pytest.mark.asyncio
async def test_logout_all_revokes_current_session(
    db_session,
    auth_client,
):
    code_response = await request_login_code(auth_client, 740000006)
    assert code_response.status_code == 200

    response = await exchange_code(
        auth_client,
        code_response.json()["code"],
    )
    assert response.status_code == 200

    session = await db_session.scalar(
        select(AuthSession).where(
            AuthSession.user_id == response.json()["id"]
        )
    )
    assert session is not None

    logout_response = await auth_client.post("/auth/logout-all")
    assert logout_response.status_code == 204

    await db_session.refresh(session)
    assert session.revoked_at is not None

    me_response = await auth_client.get("/users/me")
    assert me_response.status_code == 401


@pytest.mark.asyncio
async def test_existing_telegram_user_name_is_updated(
    db_session,
    auth_client,
):
    user = User(
        telegram_id=740000007,
        first_name="Old name",
    )
    db_session.add(user)
    await db_session.flush()

    response = await request_login_code(auth_client, user.telegram_id)

    assert response.status_code == 200

    await db_session.refresh(user)
    assert user.first_name == "Auth test user"


@pytest.mark.asyncio
async def test_new_login_code_invalidates_previous_code(
    auth_client,
    monkeypatch,
):
    codes = iter(["111111", "222222"])
    monkeypatch.setattr(
        "app.services.auth_service.generate_login_code",
        lambda: next(codes),
    )

    first = await request_login_code(auth_client, 740000008)
    second = await request_login_code(auth_client, 740000008)

    assert first.status_code == 200
    assert second.status_code == 200

    old_response = await exchange_code(auth_client, "111111")
    assert old_response.status_code == 400

    new_response = await exchange_code(auth_client, "222222")
    assert new_response.status_code == 200


@pytest.mark.asyncio
async def test_user_deactivated_after_code_issuance_cannot_login(
    db_session,
    auth_client,
):
    code_response = await request_login_code(auth_client, 740000009)
    assert code_response.status_code == 200

    user = await db_session.scalar(
        select(User).where(User.telegram_id == 740000009)
    )
    assert user is not None

    user.is_active = False
    await db_session.flush()

    response = await exchange_code(
        auth_client,
        code_response.json()["code"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired code"


@pytest.mark.asyncio
async def test_expired_auth_session_is_rejected(
    db_session,
    auth_client,
):
    user = User(first_name="Expired session user")
    db_session.add(user)
    await db_session.flush()

    token = "expired-session-test-token"
    auth_session = AuthSession(
        user_id=user.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
    )
    db_session.add(auth_session)
    await db_session.flush()

    auth_client.cookies.set(settings.session_cookie_name, token)

    response = await auth_client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_inactive_user_with_valid_session_is_rejected(
    db_session,
    auth_client,
):
    user = User(
        first_name="Inactive session user",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()

    token = "inactive-user-session-token"
    db_session.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
    )
    await db_session.flush()

    auth_client.cookies.set(settings.session_cookie_name, token)

    response = await auth_client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_configured_telegram_admin_gets_admin_role(
    db_session,
    auth_client,
    monkeypatch,
):
    telegram_id = 740000010
    monkeypatch.setattr(settings, "admin_telegram_id", telegram_id)

    response = await request_login_code(auth_client, telegram_id)

    assert response.status_code == 200

    user = await db_session.scalar(
        select(User).where(User.telegram_id == telegram_id)
    )

    assert user is not None
    assert user.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_blocked_client_cannot_exchange_login_code(
    auth_client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.auth_service.login_limiter.is_blocked",
        lambda client_key: True,
    )

    response = await exchange_code(auth_client, "123456")

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Too many failed attempts, try again later"
    )


@pytest.mark.asyncio
async def test_logout_without_cookie_returns_no_content(auth_client):
    response = await auth_client.post("/auth/logout")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_all_revokes_multiple_sessions(
    db_session,
    auth_client,
):
    telegram_id = 740000011

    first_code = await request_login_code(auth_client, telegram_id)
    assert first_code.status_code == 200

    first_login = await exchange_code(
        auth_client,
        first_code.json()["code"],
    )
    assert first_login.status_code == 200

    second_code = await request_login_code(auth_client, telegram_id)
    assert second_code.status_code == 200

    second_login = await exchange_code(
        auth_client,
        second_code.json()["code"],
    )
    assert second_login.status_code == 200

    user_id = second_login.json()["id"]

    sessions = list(
        (
            await db_session.scalars(
                select(AuthSession).where(AuthSession.user_id == user_id)
            )
        ).all()
    )
    assert len(sessions) == 2
    assert all(session.revoked_at is None for session in sessions)

    response = await auth_client.post("/auth/logout-all")

    assert response.status_code == 204

    for session in sessions:
        await db_session.refresh(session)
        assert session.revoked_at is not None

    me_response = await auth_client.get("/users/me")
    assert me_response.status_code == 401


@pytest.mark.asyncio
async def test_login_code_generation_fails_after_collision_retries(
    db_session,
    auth_client,
    monkeypatch,
):
    existing_user = User(
        telegram_id=740000012,
        first_name="Existing code owner",
    )
    db_session.add(existing_user)
    await db_session.flush()

    db_session.add(
        LoginCode(
            user_id=existing_user.id,
            code_hash=hash_login_code("123456"),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
    )
    await db_session.flush()

    monkeypatch.setattr(
        "app.services.auth_service.generate_login_code",
        lambda: "123456",
    )

    response = await request_login_code(auth_client, 740000013)

    assert response.status_code == 503
    assert response.json()["detail"] == "Try again in a moment"


@pytest.mark.asyncio
async def test_repeated_invalid_codes_block_client(auth_client):
    for _ in range(settings.login_max_failures):
        response = await exchange_code(auth_client, "999999")
        assert response.status_code == 400

    response = await exchange_code(auth_client, "999999")

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Too many failed attempts, try again later"
    )