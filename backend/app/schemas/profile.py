from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class ProfileBase(BaseModel):
    education_level: int = Field(..., ge=1, le=10, description="NSQF level (1-10)")
    prior_skills: List[str] = Field(..., description="List of skills the learner already has")
    aspirations: str = Field(..., description="Career aspirations or goals")
    learning_pace: str = Field("normal", description="Learning pace: slow/normal/fast")

    @validator('learning_pace')
    def validate_learning_pace(cls, v):
        if v not in ["slow", "normal", "fast"]:
            raise ValueError("Learning pace must be one of: slow, normal, fast")
        return v

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    profile_id: Optional[int] = None
    profile: Optional[ProfileBase] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": 1,
                "profile": {
                    "education_level": 4,
                    "prior_skills": ["python", "data analysis"],
                    "aspirations": "I want to become a data scientist",
                    "learning_pace": "normal"
                }
            }
        }
