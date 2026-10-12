from .subject_router import router as subject_router
from .topic_router import router as topic_router
from .task_router import router as task_router
from .prototype_router import router as prototype_router
from .session_router import router as session_router
from .attempt_router import router as attempt_router
from .profile_router import router as profile_router
from .user_router import router as user_router


__all__ = [
    "subject_router",
    "topic_router",
    "task_router",
    "prototype_router",
    "session_router",
    "attempt_router",
    "profile_router",
    "user_router",
]
