from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import db_helper
from app.models.user import User, UserRole
from app.security import verify_bot_key
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.services.user_service import UserService

get_db = db_helper.session_getter


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def require_bot(x_bot_key: str = Header(default="")) -> None:
    if not verify_bot_key(x_bot_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bot key")


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await auth_service.get_user_by_session_token(token)


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user