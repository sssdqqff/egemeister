from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.prototype_repository import PrototypeRepository
from app.schemas.prototype import PrototypeCreate, PrototypeResponse, PrototypeUpdate


class PrototypeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prototype_repository = PrototypeRepository(db)

    async def get_all_prototypes(self, exam_number: Optional[int] = None) -> List[PrototypeResponse]:
        prototypes = await self.prototype_repository.get_all_prototypes(exam_number=exam_number)
        return [PrototypeResponse.model_validate(prototype) for prototype in prototypes]

    async def get_prototype_by_id(self, prototype_id: int) -> PrototypeResponse:
        prototype = await self.prototype_repository.get_by_id(prototype_id)
        if not prototype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        return PrototypeResponse.model_validate(prototype)

    async def create_prototype(self, prototype_data: PrototypeCreate) -> PrototypeResponse:
        if await self.prototype_repository.get_by_code(prototype_data.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prototype with this code already exists")
        try:
            prototype = await self.prototype_repository.create_prototype(prototype_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prototype already exists")
        return PrototypeResponse.model_validate(prototype)

    async def update_prototype(self, prototype_id: int, prototype_data: PrototypeUpdate) -> PrototypeResponse:
        if prototype_data.code is not None:
            existing = await self.prototype_repository.get_by_code(prototype_data.code)
            if existing and existing.id != prototype_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prototype with this code already exists")
        try:
            prototype = await self.prototype_repository.update_prototype(prototype_id, prototype_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prototype already exists")
        if not prototype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        return PrototypeResponse.model_validate(prototype)

    
    async def deactivate_prototype(self, prototype_id: int) -> None:
        deactivated = await self.prototype_repository.deactivate_prototype(prototype_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        await self.db.commit()


    async def activate_prototype(self, prototype_id: int) -> None:
        activated = await self.prototype_repository.activate_prototype(prototype_id)
        if not activated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        await self.db.commit()


    async def delete_prototype_permanently(self, prototype_id: int) -> None:
        prototype = await self.prototype_repository.get_by_id(prototype_id)
        if not prototype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prototype not found")
        if await self.prototype_repository.has_tasks(prototype_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Prototype has tasks and cannot be deleted",
            )
        try:
            await self.prototype_repository.delete_prototype_permanently(prototype_id)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Prototype is referenced by other records and cannot be deleted",
            )
