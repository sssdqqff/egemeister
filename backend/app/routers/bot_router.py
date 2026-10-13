from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service, require_bot
from app.schemas.auth import BotLoginCodeRequest, BotLoginCodeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/internal/bot", tags=["bot"], dependencies=[Depends(require_bot)])


@router.post("/login-codes", response_model=BotLoginCodeResponse)
async def create_login_code(
    data: BotLoginCodeRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.issue_login_code(data.telegram_id, data.first_name)