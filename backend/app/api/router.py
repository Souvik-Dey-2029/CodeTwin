from fastapi import APIRouter
from app.api import repositories

api_router = APIRouter()
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
