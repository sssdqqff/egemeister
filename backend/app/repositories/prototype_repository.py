from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prototype import Prototype
from app.schemas.prototype import PrototypeCreate, PrototypeUpdate

from app.models.task import Task


class PrototypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_prototypes(self, exam_number: Optional[int] = None) -> List[Prototype]:
        stmt = select(Prototype).order_by(Prototype.exam_number, Prototype.name)
        if exam_number is not None:
            stmt = stmt.where(Prototype.exam_number == exam_number)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, prototype_id: int) -> Optional[Prototype]:
        return await self.db.get(Prototype, prototype_id)

    async def get_by_code(self, code: str) -> Optional[Prototype]:
        result = await self.db.execute(select(Prototype).where(Prototype.code == code))
        return result.scalar_one_or_none()

    async def create_prototype(self, prototype_data: PrototypeCreate) -> Prototype:
        new_prototype = Prototype(**prototype_data.model_dump())
        self.db.add(new_prototype)
        await self.db.flush()
        await self.db.refresh(new_prototype)
        return new_prototype

    async def update_prototype(self, prototype_id: int, prototype_data: PrototypeUpdate) -> Optional[Prototype]:
        prototype = await self.get_by_id(prototype_id)
        if not prototype:
            return None
        for key, value in prototype_data.model_dump(exclude_unset=True).items():
            setattr(prototype, key, value)
        await self.db.flush()
        await self.db.refresh(prototype)
        return prototype

    async def deactivate_prototype(self, prototype_id: int) -> bool:
        prototype = await self.get_by_id(prototype_id)
        if not prototype:
            return False
        prototype.is_active = False
        await self.db.flush()
        return True

    async def activate_prototype(self, prototype_id: int) -> bool:
        prototype = await self.get_by_id(prototype_id)
        if not prototype:
            return False
        prototype.is_active = True
        await self.db.flush()
        return True

    async def has_tasks(self, prototype_id: int) -> bool:
        stmt = select(Task.id).where(Task.prototype_id == prototype_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_prototype_permanently(self, prototype_id: int) -> bool:
        prototype = await self.get_by_id(prototype_id)
        if not prototype:
            return False
        await self.db.delete(prototype)
        await self.db.flush()
        return True
