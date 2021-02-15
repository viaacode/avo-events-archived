from fastapi import APIRouter

from app.api.routers import health, event

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(event.router, prefix="/event", tags=["event"])
