from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..db.database import get_db
from ..models import LearningPath, User
from ..schemas.learning_path import (
    LearningPath as LearningPathSchema,
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathItem as LearningPathItemSchema,
    LearningPathItemCreate,
    LearningPathStatus
)
from ..services.learning_path_service import (
    get_learning_paths as service_get_learning_paths,
    get_learning_path as service_get_learning_path,
    create_learning_path as service_create_learning_path,
    update_learning_path as service_update_learning_path,
    delete_learning_path as service_delete_learning_path,
    create_learning_path_item as service_create_learning_path_item,
    generate_learning_path_recommendations as service_generate_learning_path_recommendations
)
from ..services.user_service import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[LearningPathSchema])
def read_learning_paths(
    skip: int = 0, 
    limit: int = 100,
    status: LearningPathStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve learning paths for the current user, optionally filtered by status.
    """
    query = db.query(LearningPath).filter(LearningPath.user_id == current_user.id)
    
    if status:
        query = query.filter(LearningPath.status == status)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=LearningPathSchema, status_code=status.HTTP_201_CREATED)
def create_learning_path(
    learning_path: LearningPathCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new learning path for the current user.
    """
    return service_create_learning_path(db=db, path=learning_path, user_id=current_user.id)

@router.get("/{path_id}", response_model=LearningPathSchema)
def read_learning_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific learning path by ID.
    """
    return service_get_learning_path(db=db, path_id=path_id, user_id=current_user.id)

@router.put("/{path_id}", response_model=LearningPathSchema)
def update_learning_path(
    path_id: int,
    learning_path: LearningPathUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a learning path.
    """
    return service_update_learning_path(
        db=db, 
        path_id=path_id, 
        path_update=learning_path, 
        user_id=current_user.id
    )

@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a learning path.
    """
    service_delete_learning_path(db=db, path_id=path_id, user_id=current_user.id)
    return None

@router.post("/{path_id}/items", response_model=LearningPathItemSchema, status_code=status.HTTP_201_CREATED)
def add_learning_path_item(
    path_id: int,
    item: LearningPathItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add an item to a learning path.
    """
    # Verify the learning path exists and belongs to the user
    path = service_get_learning_path(db=db, path_id=path_id, user_id=current_user.id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    return service_create_learning_path_item(db=db, item=item, path_id=path_id)

@router.post("/generate", response_model=LearningPathSchema)
def generate_learning_path(
    topic: str,
    current_level: str = "beginner",
    time_commitment: str = "medium",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a personalized learning path using AI.
    """
    try:
        # Generate the learning path recommendations
        learning_path = service_generate_learning_path_recommendations(
            db=db,
            user_id=current_user.id,
            topic=topic,
            current_level=current_level,
            time_commitment=time_commitment
        )
        
        # Create the learning path in the database
        return service_create_learning_path(
            db=db,
            path=learning_path,
            user_id=current_user.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
