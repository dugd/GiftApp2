from fastapi import APIRouter
from app.api.v1.features.auth.endpoints import router as auth_router
from app.api.v1.features.recipients.endpoints import router as recipient_router
from app.api.v1.features.events.endpoints import router as event_router
from app.api.v1.features.ideas.endpoints import router as idea_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(recipient_router)
api_router.include_router(event_router)
api_router.include_router(idea_router)