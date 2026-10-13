from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.topic_service import TopicService
from app.schemas.topic import TopicResponse, TopicCreate, TopicUpdate


router = APIRouter(prefix="/topics", tags=["topics"])


async def get_topic_service(db: AsyncSession = Depends(get_db)):
    return TopicService(db)


@router.get("", response_model=list[TopicResponse], status_code=status.HTTP_200_OK)
async def get_topics(service: TopicService = Depends(get_topic_service)):
    return await service.get_all_topics()


@router.get("/{topic_id}", response_model=TopicResponse, status_code=status.HTTP_200_OK)
async def get_topic_by_id(topic_id: int, service: TopicService = Depends(get_topic_service)):
    return await service.get_topic_by_id(topic_id)


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(topic_data: TopicCreate, service: TopicService = Depends(get_topic_service)):
    return await service.create_topic(topic_data)


@router.patch("/{topic_id}", response_model=TopicResponse, status_code=status.HTTP_200_OK)
async def update_topic(topic_id: int, topic_data: TopicUpdate, service: TopicService = Depends(get_topic_service)):
    return await service.update_topic(topic_id, topic_data)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: int, service: TopicService = Depends(get_topic_service)):
    await service.deactivate_topic(topic_id)

@router.patch(
    "/{topic_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate_topic(
    topic_id: int,
    service: TopicService = Depends(get_topic_service),
) -> None:
    await service.activate_topic(topic_id)

@router.delete("/{topic_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic_permanently(
    topic_id: int,
    service: TopicService = Depends(get_topic_service),
) -> None:
    await service.delete_topic_permanently(topic_id)