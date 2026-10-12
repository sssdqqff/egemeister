from typing import List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.prototype_repository import PrototypeRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repository = TaskRepository(db)
        self.topic_repository = TopicRepository(db)
        self.prototype_repository = PrototypeRepository(db)

    async def _validate_topic_and_prototype(self, topic_id: int, prototype_id: int) -> None:
        topic = await self.topic_repository.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        prototype = await self.prototype_repository.get_by_id(prototype_id)
        if not prototype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        if prototype.exam_number != topic.number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prototype does not belong to this topic",
            )

    async def get_all_tasks(
        self,
        topic_id: Optional[int] = None,
        prototype_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TaskResponse]:
        tasks = await self.task_repository.get_all_tasks(
            topic_id=topic_id,
            prototype_id=prototype_id,
            difficulty=difficulty,
            only_active=only_active,
            limit=limit,
            offset=offset,
        )
        return [TaskResponse.model_validate(task) for task in tasks]

    async def get_task_by_id(self, task_id: int) -> TaskResponse:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse.model_validate(task)

    async def get_random_tasks(
        self,
        topic_id: int,
        count: int,
        prototype_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Sequence[int] = (),
    ) -> List[TaskResponse]:
        if not await self.topic_repository.get_by_id(topic_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        tasks = await self.task_repository.get_random_tasks(
            topic_id=topic_id,
            count=count,
            prototype_id=prototype_id,
            difficulty=difficulty,
            exclude_ids=exclude_ids,
        )
        return [TaskResponse.model_validate(task) for task in tasks]

    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        await self._validate_topic_and_prototype(task_data.topic_id, task_data.prototype_id)
        try:
            task = await self.task_repository.create_task(task_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task could not be created")
        return TaskResponse.model_validate(task)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        changes = task_data.model_dump(exclude_unset=True)
        if "topic_id" in changes or "prototype_id" in changes:
            await self._validate_topic_and_prototype(
                changes.get("topic_id", task.topic_id),
                changes.get("prototype_id", task.prototype_id),
            )
        try:
            updated_task = await self.task_repository.update_task(task_id, task_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task could not be updated")
        return TaskResponse.model_validate(updated_task)

    async def deactivate_task(self, task_id: int) -> None:
        deactivated = await self.task_repository.deactivate_task(task_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        await self.db.commit()