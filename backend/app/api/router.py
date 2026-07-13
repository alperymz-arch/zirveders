from fastapi import APIRouter

from app.api.routes import accounting, auth, health, settings, users

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(accounting.router)
api_router.include_router(settings.router)
