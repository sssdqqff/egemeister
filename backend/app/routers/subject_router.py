from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.subject_service import SubjectService
from app.schemas.subject import SubjectResponse, SubjectCreate, SubjectUpdate


router = APIRouter(prefix="/subjects", tags=["subjects"])


async def get_subject_service(db: AsyncSession = Depends(get_db)):
    return SubjectService(db)


@router.get("", response_model=list[SubjectResponse], status_code=status.HTTP_200_OK)
async def get_subjects(service: SubjectService = Depends(get_subject_service)):
    return await service.get_all_subjects()


@router.get("/{subject_id}", response_model=SubjectResponse, status_code=status.HTTP_200_OK)
async def get_subject_by_id(subject_id: int, service: SubjectService = Depends(get_subject_service)):
    return await service.get_subject_by_id(subject_id)


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(subject_data: SubjectCreate, service: SubjectService = Depends(get_subject_service)):
    return await service.create_subject(subject_data)


@router.patch("/{subject_id}", response_model=SubjectResponse, status_code=status.HTTP_200_OK)
async def update_subject(subject_id: int, subject_data: SubjectUpdate, service: SubjectService = Depends(get_subject_service)):
    return await service.update_subject(subject_id, subject_data)


@router.patch("/{subject_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service)
):
    await service.activate_subject(subject_id)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: int, service: SubjectService = Depends(get_subject_service)):
    await service.deactivate_subject(subject_id)


@router.delete("/{subject_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject_permanently(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
):
    await service.delete_subject_permanently(subject_id)