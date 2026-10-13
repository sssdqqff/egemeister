from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.services.prototype_service import PrototypeService
from app.schemas.prototype import PrototypeResponse, PrototypeCreate, PrototypeUpdate


router = APIRouter(prefix="/prototypes", tags=["prototypes"])
admin_only = [Depends(get_current_admin)]


async def get_prototype_service(db: AsyncSession = Depends(get_db)):
    return PrototypeService(db)


@router.get("", response_model=list[PrototypeResponse], status_code=status.HTTP_200_OK)
async def get_prototypes(service: PrototypeService = Depends(get_prototype_service)):
    return await service.get_all_prototypes()


@router.get("/{prototype_id}", response_model=PrototypeResponse, status_code=status.HTTP_200_OK)
async def get_prototype_by_id(prototype_id: int, service: PrototypeService = Depends(get_prototype_service)):
    return await service.get_prototype_by_id(prototype_id)


@router.post("", response_model=PrototypeResponse, status_code=status.HTTP_201_CREATED, dependencies=admin_only)
async def create_prototype(prototype_data: PrototypeCreate, service: PrototypeService = Depends(get_prototype_service)):
    return await service.create_prototype(prototype_data)


@router.patch("/{prototype_id}", response_model=PrototypeResponse, status_code=status.HTTP_200_OK, dependencies=admin_only)
async def update_prototype(prototype_id: int, prototype_data: PrototypeUpdate, service: PrototypeService = Depends(get_prototype_service)):
    return await service.update_prototype(prototype_id, prototype_data)


@router.patch("/{prototype_id}/activate", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin_only)
async def activate_prototype(prototype_id: int, service: PrototypeService = Depends(get_prototype_service)):
    await service.activate_prototype(prototype_id)


@router.delete("/{prototype_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin_only)
async def delete_prototype(prototype_id: int, service: PrototypeService = Depends(get_prototype_service)):
    await service.deactivate_prototype(prototype_id)


@router.delete("/{prototype_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin_only)
async def delete_prototype_permanently(prototype_id: int, service: PrototypeService = Depends(get_prototype_service)):
    await service.delete_prototype_permanently(prototype_id)