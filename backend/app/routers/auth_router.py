from fastapi import APIRouter, Depends, Request, Response, status

from app.config import settings
from app.dependencies import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import CodeExchangeRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


@router.post("/telegram/exchange", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def exchange_code(
    data: CodeExchangeRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    client_key = request.client.host if request.client else "unknown"
    user, token = await service.exchange_code(data.code, client_key)
    set_session_cookie(response, token)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        await service.logout(token)
    clear_session_cookie(response)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout_everywhere(user.id)
    clear_session_cookie(response)