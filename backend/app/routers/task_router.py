from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.task_service import TaskService
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service(db: AsyncSession = Depends(get_db)):
    return TaskService(db)


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def get_tasks(service: TaskService = Depends(get_task_service)):
    return await service.get_all_tasks()


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task_by_id(task_id: int, service: TaskService = Depends(get_task_service)):
    return await service.get_task_by_id(task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, service: TaskService = Depends(get_task_service)):
    return await service.create_task(task_data)


@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_data: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return await service.update_task(task_id, task_data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    await service.delete_task(task_id)


@router.delete("/{task_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_permanently(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete_task_permanently(task_id)