from fastapi import APIRouter

from .endpoints import test, areas, openai_chat

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(openai_chat.router, prefix="/openai", tags=["OpenAI Chat"])
