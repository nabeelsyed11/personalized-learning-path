from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app import schemas, crud
from app.services.recommender import HybridRecommender

router = APIRouter()

@router.post("/recommend", status_code=status.HTTP_200_OK)
async def get_recommendations(
    request: schemas.RecommendationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get personalized learning path recommendations.
    
    Either provide a profile_id or a complete profile in the request body.
    """
    if request.profile_id:
        profile = crud.get_profile(db, profile_id=request.profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        profile_data = schemas.Profile.from_orm(profile).dict()
    elif request.profile:
        profile_data = request.profile.dict()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either profile_id or profile must be provided"
        )
    
    # Initialize and use the recommender
    recommender = HybridRecommender()
    recommendations = recommender.compute_recommendations(profile_data)
    
    # Store the recommendation if we have a profile_id
    recommendation_id = None
    if request.profile_id:
        recommendation_id = crud.create_recommendation(
            db=db,
            profile_id=request.profile_id,
            recommendations=recommendations
        )
    
    return {
        "recommendation_id": recommendation_id,
        "recommendations": recommendations
    }
