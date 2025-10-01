from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, models
from app.schemas import NSQFCourse as NSQFCourseSchema
from typing import List

router = APIRouter()

@router.get("/courses", response_model=List[NSQFCourseSchema])
def get_courses(db: Session = Depends(get_db)):
    """
    Get all available NSQF courses.
    
    Returns a list of courses with their details including NSQF level, qualification,
    example courses, and description.
    """
    return crud.get_nsqf_courses(db)
