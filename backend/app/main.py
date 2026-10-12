from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.routers.subject_router import router as subject_router
from app.routers.topic_router import router as topic_router
from app.routers.task_router import router as task_router
from app.routers.prototype_router import router as prototype_router
from app.routers.session_router import router as session_router
from app.routers.attempt_router import router as attempt_router
from app.routers.profile_router import router as profile_router
from app.routers.user_router import router as user_router

app = FastAPI(
    title=settings.app_name,
    description="Platform for EGE preparation",
    version="0.1.0",
    debug=settings.debug_mode,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the hell"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(subject_router)
app.include_router(topic_router)
app.include_router(task_router)
app.include_router(prototype_router)
app.include_router(session_router)
app.include_router(attempt_router)
app.include_router(profile_router)
app.include_router(user_router)