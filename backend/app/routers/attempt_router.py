from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.attempt_service import AttemptService
from app.schemas.attempt import AttemptResponse, AttemptCreate


router = APIRouter(prefix="/attempts", tags=["attempts"])


async def get_attempt_service(db: AsyncSession = Depends(get_db)):
    return AttemptService(db)


@router.get("", response_model=list[AttemptResponse], status_code=status.HTTP_200_OK)
async def get_attempts(
    user: User = Depends(get_current_user),
    service: AttemptService = Depends(get_attempt_service),
):
    return await service.get_user_attempts(user.id)


@router.get("/{attempt_id}", response_model=AttemptResponse, status_code=status.HTTP_200_OK)
async def get_attempt_by_id(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: AttemptService = Depends(get_attempt_service),
):
    return await service.get_user_attempt_by_id(attempt_id, user.id)


@router.post("", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_attempt(
    attempt_data: AttemptCreate,
    user: User = Depends(get_current_user),
    service: AttemptService = Depends(get_attempt_service),
):
    return await service.create_attempt(user.id, attempt_data)
