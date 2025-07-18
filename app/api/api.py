from fastapi import APIRouter
from app.api.endpoints import users, sites, floors

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(floors.router, prefix="/floors", tags=["floors"]) 