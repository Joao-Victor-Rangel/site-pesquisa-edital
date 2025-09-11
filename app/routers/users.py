from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.schemas import User as UserSchema, UserUpdate
from app.core.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/stats")
def get_user_stats(current_user: User = Depends(get_current_user)):
    # Mock stats - in production, calculate from database
    return {
        "opportunities_viewed": 47,
        "applications_submitted": 12,
        "success_rate": 25.0,
        "favorites_count": 8,
        "alerts_received": 156
    }