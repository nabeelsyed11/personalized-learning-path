from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app import crud, schemas
from app.services.ai_agent import ai_agent

router = APIRouter()

# System prompt for the learning assistant
SYSTEM_PROMPT = """You are a helpful learning assistant that helps users navigate their personalized learning path. 
You have access to the user's profile and learning recommendations. 
Be supportive, encouraging, and provide specific guidance based on the user's context.
If the user asks about their learning path, refer to their recommendations.
Keep responses concise and focused on learning and skill development."""

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_llm(
    chat: schemas.ChatMessage,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Chat with the learning assistant.
    
    This endpoint accepts a message and an optional profile_id for context,
    and returns a response from the learning assistant.
    """
    context = {}
    
    # Add profile and recommendation context if profile_id is provided
    if chat.profile_id:
        # Get the latest recommendations for this profile
        recommendations = crud.get_recommendations_by_profile(
            db, 
            profile_id=chat.profile_id,
            limit=1
        )
        
        if recommendations:
            context["recommendations"] = [
                {
                    "recommended_job_roles": rec.recommendations.get("recommended_job_roles", []),
                    "pathway": rec.recommendations.get("pathway", []),
                    "generated_at": rec.created_at.isoformat()
                }
                for rec in recommendations
            ]
        
        # Get profile details
        profile = crud.get_profile(db, profile_id=chat.profile_id)
        if profile:
            context["profile"] = {
                "education_level": profile.education_level,
                "prior_skills": profile.prior_skills,
                "aspirations": profile.aspirations,
                "learning_pace": profile.learning_pace
            }
    
    # Generate response using the AI agent
    response = await ai_agent.call_llm(
        message=chat.message,
        system_prompt=SYSTEM_PROMPT,
        context=context
    )
    
    # Generate some suggested follow-up questions
    suggested_responses = generate_suggested_responses(chat.message, context)
    
    return {
        "message": chat.message,
        "response": response,
        "suggested_responses": suggested_responses,
        "timestamp": datetime.utcnow().isoformat(),
        "context_used": bool(context)  # Indicate if profile context was used
    }

def generate_suggested_responses(message: str, context: Dict) -> List[str]:
    """Generate suggested follow-up questions based on the message and context."""
    message_lower = message.lower()
    suggestions = []
    
    # General suggestions
    if any(word in message_lower for word in ["learn", "study", "skill"]):
        suggestions.extend([
            "What are the prerequisites for this topic?",
            "How long will it take to learn this?",
            "Can you recommend learning resources?"
        ])
    
    # If we have recommendations in context
    if context.get("recommendations"):
        recs = context["recommendations"][0]
        
        if recs.get("recommended_job_roles"):
            job = recs["recommended_job_roles"][0]
            suggestions.append(f"What skills do I need to become a {job}?")
        
        if recs.get("pathway"):
            next_step = recs["pathway"][0].get("title", "next step")
            suggestions.append(f"Tell me more about {next_step}")
    
    # Add some general suggestions if we don't have enough
    while len(suggestions) < 3:
        general = [
            "What's the best way to track my progress?",
            "How can I stay motivated while learning?",
            "Can you explain this in simpler terms?",
            "What are some practical projects I can work on?"
        ]
        for s in general:
            if s not in suggestions and len(suggestions) < 3:
                suggestions.append(s)
            
    return suggestions[:3]  # Return max 3 suggestions
