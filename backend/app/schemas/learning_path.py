from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LearningPathStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class LearningPathItemType(str, Enum):
    COURSE = "course"
    ARTICLE = "article"
    VIDEO = "video"
    EXERCISE = "exercise"
    PROJECT = "project"

# Shared properties
class LearningPathItemBase(BaseModel):
    item_type: LearningPathItemType
    title: str
    description: Optional[str] = None
    resource_url: Optional[str] = None
    estimated_duration: Optional[int] = None
    order: int = 0
    is_completed: bool = False

# Properties to receive on item creation
class LearningPathItemCreate(LearningPathItemBase):
    pass

# Properties to receive on item update
class LearningPathItemUpdate(LearningPathItemBase):
    pass

# Properties shared by models stored in DB
class LearningPathItemInDBBase(LearningPathItemBase):
    id: int
    learning_path_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class LearningPathItem(LearningPathItemInDBBase):
    pass

# Shared properties
class LearningPathBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: LearningPathStatus = LearningPathStatus.DRAFT

# Properties to receive on learning path creation
class LearningPathCreate(LearningPathBase):
    items: List[LearningPathItemCreate] = []

# Properties to receive on learning path update
class LearningPathUpdate(LearningPathBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LearningPathStatus] = None

# Properties shared by models stored in DB
class LearningPathInDBBase(LearningPathBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[LearningPathItem] = []

    class Config:
        from_attributes = True

# Properties to return to client
class LearningPath(LearningPathInDBBase):
    pass

# Properties stored in DB
class LearningPathInDB(LearningPathInDBBase):
    pass
