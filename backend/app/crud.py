from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def create_profile(db: Session, profile: schemas.ProfileCreate) -> models.Profile:
    """Create a new learner profile."""
    db_profile = models.Profile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_profile(db: Session, profile_id: int) -> Optional[models.Profile]:
    """Retrieve a profile by ID."""
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()

def create_recommendation(
    db: Session, 
    profile_id: int, 
    recommendations: dict
) -> int:
    """Store a recommendation snapshot in the database."""
    db_recommendation = models.Recommendation(
        profile_id=profile_id,
        recommendations=recommendations
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation.id

def get_nsqf_courses(db: Session) -> List[models.NSQFCourse]:
    """Retrieve all NSQF courses."""
    return db.query(models.NSQFCourse).all()

def get_recommendation(db: Session, recommendation_id: int) -> Optional[models.Recommendation]:
    """Retrieve a recommendation by ID."""
    return db.query(models.Recommendation).filter(
        models.Recommendation.id == recommendation_id
    ).first()

def get_recommendations_by_profile(
    db: Session, 
    profile_id: int, 
    limit: int = 1
) -> List[models.Recommendation]:
    """
    Retrieve the most recent recommendations for a profile.
    
    Args:
        db: Database session
        profile_id: ID of the profile
        limit: Maximum number of recommendations to return
        
    Returns:
        List of Recommendation objects, ordered by most recent first
    """
    return (
        db.query(models.Recommendation)
        .filter(models.Recommendation.profile_id == profile_id)
        .order_by(models.Recommendation.created_at.desc())
        .limit(limit)
        .all()
    )
