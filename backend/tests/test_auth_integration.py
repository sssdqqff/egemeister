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
from app.models.user import User
from app.security import hash_login_code


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