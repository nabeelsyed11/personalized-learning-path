from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, crud

router = APIRouter()

@router.post("/profile", response_model=schemas.Profile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    """
    Create a new learner profile.
    
    - **education_level**: NSQF level (1-10)
    - **prior_skills**: List of skills the learner already has
    - **aspirations**: Career aspirations or goals
    - **learning_pace**: Learning pace (slow/normal/fast)
    """
    return crud.create_profile(db=db, profile=profile)
