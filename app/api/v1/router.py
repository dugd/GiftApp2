from fastapi import APIRouter

from .features.auth import router as auth_router
from .features.recipients import router as recipient_router
from .features.events import router as event_router
from .features.ideas import router as idea_router
from .features.media import router as media_router
from .features.users import router as user_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(recipient_router)
api_router.include_router(event_router)
api_router.include_router(idea_router)
api_router.include_router(media_router)
