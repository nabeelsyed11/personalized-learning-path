from fastapi import APIRouter
from .profile import router as profile_router
from .recommend import router as recommend_router
from .courses import router as courses_router
from .chat import router as chat_router

# Create a router for each endpoint
router = APIRouter()
router.include_router(profile_router, prefix="/profile", tags=["profiles"])
router.include_router(recommend_router, prefix="/recommend", tags=["recommendations"])
router.include_router(courses_router, prefix="/courses", tags=["courses"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
