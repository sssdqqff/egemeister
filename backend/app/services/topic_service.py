from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.subject_repository import SubjectRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.topic import TopicCreate, TopicResponse, TopicUpdate


class TopicService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.topic_repository = TopicRepository(db)
        self.subject_repository = SubjectRepository(db)

    async def get_all_topics(self, subject_id: Optional[int] = None, only_active: bool = True) -> List[TopicResponse]:
        topics = await self.topic_repository.get_all_topics(subject_id=subject_id, only_active=only_active)
        return [TopicResponse.model_validate(topic) for topic in topics]

    async def get_topic_by_id(self, topic_id: int) -> TopicResponse:
        topic = await self.topic_repository.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        return TopicResponse.model_validate(topic)

    async def create_topic(self, topic_data: TopicCreate) -> TopicResponse:
        if not await self.subject_repository.get_by_id(topic_data.subject_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        if await self.topic_repository.get_by_subject_and_number(topic_data.subject_id, topic_data.number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic with this number already exists in the subject")
        if await self.topic_repository.get_by_subject_and_slug(topic_data.subject_id, topic_data.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic with this slug already exists in the subject")
        try:
            topic = await self.topic_repository.create_topic(topic_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic already exists")
        return TopicResponse.model_validate(topic)

    async def update_topic(self, topic_id: int, topic_data: TopicUpdate) -> TopicResponse:
        topic = await self.topic_repository.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        changes = topic_data.model_dump(exclude_unset=True)
        if "number" in changes:
            existing = await self.topic_repository.get_by_subject_and_number(topic.subject_id, changes["number"])
            if existing and existing.id != topic_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic with this number already exists in the subject")
        if "slug" in changes:
            existing = await self.topic_repository.get_by_subject_and_slug(topic.subject_id, changes["slug"])
            if existing and existing.id != topic_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic with this slug already exists in the subject")
        try:
            updated_topic = await self.topic_repository.update_topic(topic_id, topic_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic already exists")
        return TopicResponse.model_validate(updated_topic)

    async def deactivate_topic(self, topic_id: int) -> None:
        deactivated = await self.topic_repository.deactivate_topic(topic_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        await self.db.commit()

    async def activate_topic(self, topic_id: int) -> None:
        activated = await self.topic_repository.activate_topic(topic_id)

        if not activated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        await self.db.commit()