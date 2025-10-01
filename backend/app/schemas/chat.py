from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., description="The message content")
    profile_id: Optional[int] = Field(
        None, 
        description="Optional profile ID for personalized context"
    )

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    message: str = Field(..., description="The user's original message")
    response: str = Field(..., description="The assistant's response")
    suggested_responses: List[str] = Field(
        default_factory=list,
        description="List of suggested follow-up questions"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp of the response"
    )
    context_used: bool = Field(
        False,
        description="Whether profile context was used in the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What should I learn next?",
                "response": "Based on your profile, I recommend focusing on Python fundamentals. This will provide a strong foundation for your data science goals.",
                "suggested_responses": [
                    "What are the best resources for learning Python?",
                    "How long will it take to become proficient?",
                    "Can you suggest a learning schedule?"
                ],
                "timestamp": "2023-10-01T12:00:00.000Z",
                "context_used": True
            }
        }
