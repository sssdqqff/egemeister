import hashlib
import hmac
import secrets

from app.config import settings


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_login_code() -> str:
    return str(secrets.randbelow(10 ** settings.login_code_length)).zfill(settings.login_code_length)


def hash_login_code(code: str) -> str:
    message = f"login-code:{code}".encode()
    return hmac.new(settings.secret_key.encode(), message, hashlib.sha256).hexdigest()


def verify_bot_key(provided_key: str) -> bool:
    return hmac.compare_digest(provided_key.encode(), settings.bot_api_key.encode())