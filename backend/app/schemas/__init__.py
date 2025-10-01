from pydantic import BaseModel

from .profile import ProfileBase, ProfileCreate, Profile, RecommendationRequest
from .chat import ChatMessage, ChatResponse
from .learning_path import (
    LearningPathStatus,
    LearningPathItemType,
    LearningPathItemBase,
    LearningPathItemCreate,
    LearningPathItemUpdate,
    LearningPathItemInDBBase,
    LearningPathItem,
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathInDBBase,
    LearningPath,
    LearningPathInDB
)

# Course schema
class NSQFCourse(BaseModel):
    id: int
    title: str
    description: str
    nsqf_level: int
    duration_weeks: int
    prerequisites: List[str] = []
    learning_outcomes: List[str] = []
    job_roles: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

__all__ = [
    'ProfileBase',
    'ProfileCreate',
    'Profile',
    'RecommendationRequest',
    'ChatMessage',
    'ChatResponse',
    'NSQFCourse',
    'LearningPathStatus',
    'LearningPathItemType',
    'LearningPathItemBase',
    'LearningPathItemCreate',
    'LearningPathItemUpdate',
    'LearningPathItemInDBBase',
    'LearningPathItem',
    'LearningPathCreate',
    'LearningPathUpdate',
    'LearningPathInDBBase',
    'LearningPath',
    'LearningPathInDB'
]
