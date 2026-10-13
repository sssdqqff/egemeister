from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

from app.models.attempt import Attempt


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_tasks(
        self,
        topic_id: Optional[int] = None,
        prototype_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        stmt = select(Task).order_by(Task.id).limit(limit).offset(offset)
        if topic_id is not None:
            stmt = stmt.where(Task.topic_id == topic_id)
        if prototype_id is not None:
            stmt = stmt.where(Task.prototype_id == prototype_id)
        if difficulty is not None:
            stmt = stmt.where(Task.difficulty == difficulty)
        if only_active:
            stmt = stmt.where(Task.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_random_tasks(
        self,
        topic_id: int,
        count: int,
        prototype_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Sequence[int] = (),
    ) -> List[Task]:
        stmt = select(Task).where(Task.topic_id == topic_id, Task.is_active.is_(True))
        if prototype_id is not None:
            stmt = stmt.where(Task.prototype_id == prototype_id)
        if difficulty is not None:
            stmt = stmt.where(Task.difficulty == difficulty)
        if exclude_ids:
            stmt = stmt.where(Task.id.not_in(exclude_ids))
        stmt = stmt.order_by(func.random()).limit(count)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, task_ids: Sequence[int]) -> List[Task]:
        result = await self.db.execute(select(Task).where(Task.id.in_(task_ids)))
        return result.scalars().all()

    async def get_task_with_relations(self, task_id: int) -> Optional[Task]:
        stmt = (
            select(Task)
            .options(selectinload(Task.topic), selectinload(Task.prototype))
            .where(Task.id == task_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return await self.db.get(Task, task_id)

    async def create_task(self, task_data: TaskCreate) -> Task:
        new_task = Task(**task_data.model_dump())
        self.db.add(new_task)
        await self.db.flush()
        await self.db.refresh(new_task)
        return new_task

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None
        for key, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def deactivate_task(self, task_id: int) -> bool:
        task = await self.get_by_id(task_id)
        if not task:
            return False
        task.is_active = False
        await self.db.flush()
        return True

    async def has_attempts(self, task_id: int) -> bool:
        stmt = select(Attempt.id).where(Attempt.task_id == task_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_task_permanently(self, task: Task) -> None:
        await self.db.delete(task)
        await self.db.flush()