from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate


class TopicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_topics(self, subject_id: Optional[int] = None, only_active: bool = True) -> List[Topic]:
        stmt = select(Topic).order_by(Topic.subject_id, Topic.number)
        if subject_id is not None:
            stmt = stmt.where(Topic.subject_id == subject_id)
        if only_active:
            stmt = stmt.where(Topic.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_topic_with_tasks(self, topic_id: int) -> Optional[Topic]:
        stmt = select(Topic).options(selectinload(Topic.tasks)).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, topic_id: int) -> Optional[Topic]:
        return await self.db.get(Topic, topic_id)

    async def get_by_subject_and_number(self, subject_id: int, number: int) -> Optional[Topic]:
        stmt = select(Topic).where(Topic.subject_id == subject_id, Topic.number == number)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_subject_and_slug(self, subject_id: int, slug: str) -> Optional[Topic]:
        stmt = select(Topic).where(Topic.subject_id == subject_id, Topic.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_topic(self, topic_data: TopicCreate) -> Topic:
        new_topic = Topic(**topic_data.model_dump())
        self.db.add(new_topic)
        await self.db.flush()
        await self.db.refresh(new_topic)
        return new_topic

    async def update_topic(self, topic_id: int, topic_data: TopicUpdate) -> Optional[Topic]:
        topic = await self.get_by_id(topic_id)
        if not topic:
            return None
        for key, value in topic_data.model_dump(exclude_unset=True).items():
            setattr(topic, key, value)
        await self.db.flush()
        await self.db.refresh(topic)
        return topic

    async def deactivate_topic(self, topic_id: int) -> bool:
        topic = await self.get_by_id(topic_id)
        if not topic:
            return False
        topic.is_active = False
        await self.db.flush()
        return True