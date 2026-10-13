from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.session_service import SessionService
from app.schemas.session import SessionResponse, SessionCreate, SessionUpdate


router = APIRouter(prefix="/sessions", tags=["sessions"])


async def get_session_service(db: AsyncSession = Depends(get_db)):
    return SessionService(db)


@router.get("", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions(
    user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.get_user_sessions(user.id)


@router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def get_session_by_id(
    session_id: int,
    user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.get_session_by_id(session_id, user.id)


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.create_session(user.id, session_data)


@router.patch("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.update_user_session(session_id, user.id, session_data)


@router.patch("/{session_id}/finish", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def finish_session(
    session_id: int,
    user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.finish_session(session_id, user.id)