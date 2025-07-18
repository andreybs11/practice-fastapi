from fastapi import APIRouter
from app.api.endpoints import users

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"]) 