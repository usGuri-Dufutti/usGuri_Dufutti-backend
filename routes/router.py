from fastapi import APIRouter

from .endpoints import test, areas

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
