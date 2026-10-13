from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.subject_repository import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate


class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subject_repository = SubjectRepository(db)

    async def get_all_subjects(self, only_active: bool = True) -> List[SubjectResponse]:
        subjects = await self.subject_repository.get_all_subjects(only_active=only_active)
        return [SubjectResponse.model_validate(subject) for subject in subjects]

    async def get_subject_by_id(self, subject_id: int) -> SubjectResponse:
        subject = await self.subject_repository.get_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return SubjectResponse.model_validate(subject)

    async def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        if await self.subject_repository.get_by_name(subject_data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject with this name already exists")
        if await self.subject_repository.get_by_slug(subject_data.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject with this slug already exists")
        try:
            subject = await self.subject_repository.create_subject(subject_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject already exists")
        return SubjectResponse.model_validate(subject)

    async def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> SubjectResponse:
        if subject_data.name is not None:
            existing = await self.subject_repository.get_by_name(subject_data.name)
            if existing and existing.id != subject_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject with this name already exists")
        try:
            subject = await self.subject_repository.update_subject(subject_id, subject_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subject already exists")
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return SubjectResponse.model_validate(subject)

    async def deactivate_subject(self, subject_id: int) -> None:
        deactivated = await self.subject_repository.deactivate_subject(subject_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        await self.db.commit()

    async def activate_subject(self, subject_id: int) -> None:
        activated = await self.subject_repository.activate_subject(subject_id)
        if not activated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        await self.db.commit()