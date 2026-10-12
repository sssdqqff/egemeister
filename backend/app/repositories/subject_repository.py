from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_subjects(self, only_active: bool = True) -> List[Subject]:
        stmt = select(Subject).order_by(Subject.id)
        if only_active:
            stmt = stmt.where(Subject.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_subject_with_topics(self, subject_id: int) -> Optional[Subject]:
        stmt = select(Subject).options(selectinload(Subject.topics)).where(Subject.id == subject_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return await self.db.get(Subject, subject_id)

    async def get_by_name(self, name: str) -> Optional[Subject]:
        result = await self.db.execute(select(Subject).where(Subject.name == name))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Subject]:
        result = await self.db.execute(select(Subject).where(Subject.slug == slug))
        return result.scalar_one_or_none()

    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        new_subject = Subject(**subject_data.model_dump())
        try:
            self.db.add(new_subject)
            await self.db.commit()
            await self.db.refresh(new_subject)
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return new_subject

    async def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[Subject]:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None
        for key, value in subject_data.model_dump(exclude_unset=True).items():
            setattr(subject, key, value)
        try:
            await self.db.commit()
            await self.db.refresh(subject)
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return subject

    async def deactivate_subject(self, subject_id: int) -> bool:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return False
        try:
            subject.is_active = False
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return True