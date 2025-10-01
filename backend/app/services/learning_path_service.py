import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import openai
import os
from dotenv import load_dotenv

from ..models import LearningPath, LearningPathItem, User
from ..schemas.learning_path import LearningPathCreate, LearningPathUpdate, LearningPathItemCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Constants
VALID_SKILL_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_TIME_COMMITMENTS = ["low", "medium", "high"]
VALID_ITEM_TYPES = ["course", "article", "video", "exercise", "project"]

def get_learning_paths(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[LearningPath]:
    return db.query(LearningPath).filter(LearningPath.user_id == user_id).offset(skip).limit(limit).all()

def get_learning_path(db: Session, path_id: int, user_id: int) -> Optional[LearningPath]:
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == user_id
    ).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    return path

def create_learning_path(db: Session, path: LearningPathCreate, user_id: int) -> LearningPath:
    db_path = LearningPath(
        **path.dict(exclude={"items"}),
        user_id=user_id
    )
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    # Add items if any
    if path.items:
        for item in path.items:
            create_learning_path_item(db, item, db_path.id)
    
    return db_path

def update_learning_path(
    db: Session, 
    path_id: int, 
    path_update: LearningPathUpdate, 
    user_id: int
) -> LearningPath:
    db_path = get_learning_path(db, path_id, user_id)
    
    update_data = path_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "items":
            setattr(db_path, field, value)
    
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

def delete_learning_path(db: Session, path_id: int, user_id: int) -> LearningPath:
    db_path = get_learning_path(db, path_id, user_id)
    db.delete(db_path)
    db.commit()
    return db_path

def create_learning_path_item(
    db: Session, 
    item: LearningPathItemCreate, 
    path_id: int
) -> LearningPathItem:
    db_item = LearningPathItem(**item.dict(), learning_path_id=path_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def _validate_and_format_input(topic: str, current_level: str, time_commitment: str) -> tuple[str, str, str]:
    """Validate and format input parameters."""
    if not topic or not isinstance(topic, str) or len(topic.strip()) < 2:
        raise ValueError("Topic must be a non-empty string with at least 2 characters")
    
    current_level = current_level.lower()
    if current_level not in VALID_SKILL_LEVELS:
        logger.warning(f"Invalid skill level: {current_level}. Defaulting to 'beginner'")
        current_level = "beginner"
    
    time_commitment = time_commitment.lower()
    if time_commitment not in VALID_TIME_COMMITMENTS:
        logger.warning(f"Invalid time commitment: {time_commitment}. Defaulting to 'medium'")
        time_commitment = "medium"
    
    return topic.strip(), current_level, time_commitment

def _generate_ai_prompt(topic: str, current_level: str, time_commitment: str) -> str:
    """Generate the prompt for the AI."""
    return f"""
    Create a personalized learning path for someone who wants to learn "{topic}".
    Current skill level: {current_level}
    Time commitment: {time_commitment}
    
    Please provide a structured learning path with the following format:
    - Each item should have a type (course, article, video, exercise, project)
    - A title and description for each item
    - Estimated time to complete each item (in minutes)
    - A logical order for the items
    
    Format the response as a valid JSON array of objects with these required fields:
    - item_type: one of {VALID_ITEM_TYPES}
    - title: string
    - description: string
    - resource_url: string (can be empty)
    - estimated_duration: number (in minutes, between 5 and 240)
    - order: number (starting from 0)
    
    Example:
    [
        {{
            "item_type": "course",
            "title": "Introduction to {topic}",
            "description": "Learn the basics of {topic}...",
            "resource_url": "https://example.com/intro",
            "estimated_duration": 90,
            "order": 0
        }}
    ]
    """

def _parse_ai_response(content: str) -> List[Dict[str, Any]]:
    """Parse the AI response into a list of learning path items."""
    try:
        # Clean the response to extract just the JSON array
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end].strip()
        items = json.loads(json_str)
        
        # Validate each item
        validated_items = []
        for i, item in enumerate(items):
            if not all(k in item for k in ['item_type', 'title', 'description', 'estimated_duration', 'order']):
                logger.warning(f"Skipping invalid item at index {i}: missing required fields")
                continue
                
            if item['item_type'] not in VALID_ITEM_TYPES:
                logger.warning(f"Invalid item_type '{item['item_type']}' at index {i}")
                continue
                
            validated_items.append({
                'item_type': item['item_type'],
                'title': str(item['title']).strip(),
                'description': str(item['description']).strip(),
                'resource_url': str(item.get('resource_url', '')).strip(),
                'estimated_duration': max(5, min(240, int(item['estimated_duration']))),  # Clamp between 5-240 minutes
                'order': int(item['order'])
            })
            
        return validated_items
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Error parsing AI response: {str(e)}")
        raise ValueError("Failed to parse AI response")

def _create_default_path(topic: str, current_level: str) -> LearningPathCreate:
    """Create a default learning path when AI generation fails."""
    return LearningPathCreate(
        title=f"{topic.title()} Learning Path",
        description=f"A personalized learning path for {topic} at {current_level} level.",
        items=[
            LearningPathItemCreate(
                item_type="course",
                title=f"Introduction to {topic}",
                description=f"A comprehensive introduction to {topic} for {current_level} learners.",
                resource_url="",
                estimated_duration=120,
                order=0
            )
        ]
    )

def generate_learning_path_recommendations(
    db: Session,
    user_id: int,
    topic: str,
    current_level: str = "beginner",
    time_commitment: str = "medium"
) -> LearningPathCreate:
    """
    Generate a personalized learning path using OpenAI's API.
    
    Args:
        db: Database session
        user_id: ID of the user requesting the learning path
        topic: The topic to learn about
        current_level: Skill level (beginner, intermediate, advanced)
        time_commitment: Available time commitment (low, medium, high)
        
    Returns:
        LearningPathCreate: A learning path with generated items
        
    Raises:
        HTTPException: If there's an error generating the learning path
    """
    try:
        # Validate and format inputs
        topic, current_level, time_commitment = _validate_and_format_input(
            topic, current_level, time_commitment
        )
        
        logger.info(f"Generating learning path for topic: {topic}, level: {current_level}, time: {time_commitment}")
        
        # Generate the AI prompt
        prompt = _generate_ai_prompt(topic, current_level, time_commitment)
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=DEFAULT_OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful learning assistant that creates personalized learning paths. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse the AI response
            content = response.choices[0].message.content
            logger.debug(f"AI Response: {content}")
            
            # Parse and validate the response
            items_data = _parse_ai_response(content)
            
            if not items_data:
                logger.warning("No valid items generated, using default path")
                return _create_default_path(topic, current_level)
            
            # Create LearningPathItem objects
            items = [
                LearningPathItemCreate(
                    item_type=item["item_type"],
                    title=item["title"],
                    description=item["description"],
                    resource_url=item["resource_url"],
                    estimated_duration=item["estimated_duration"],
                    order=item["order"]
                )
                for item in items_data
            ]
            
            # Create the learning path
            return LearningPathCreate(
                title=f"{topic.title()} Learning Path",
                description=f"A personalized learning path for {topic} at {current_level} level.",
                items=items
            )
            
        except Exception as ai_error:
            logger.error(f"AI generation failed: {str(ai_error)}")
            # Fall back to default path
            return _create_default_path(topic, current_level)
            
    except ValueError as ve:
        logger.error(f"Input validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )
