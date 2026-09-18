from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
import uuid

from app.api.deps import get_db
from app.models.user_preference import UserSearchPreference
from app.schemas.user_preference import UserSearchPreferenceCreate, UserSearchPreferenceRead

router = APIRouter()

@router.post("/", response_model=UserSearchPreferenceRead, status_code=status.HTTP_201_CREATED)
async def create_user_preference(
    preference_payload: UserSearchPreferenceCreate,
    user_id: uuid.UUID = Query(..., description="user_id of the user creating this search preference"),
    db: AsyncSession = Depends(get_db)
):
    db_preference = UserSearchPreference(
        user_id = user_id,
        **preference_payload.model_dump()
    )
    
    db.add(db_preference)
    db.commit()
    
    db.refresh(db_preference)
    
    return db_preference

