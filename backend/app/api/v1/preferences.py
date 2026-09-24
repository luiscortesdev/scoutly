from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
import uuid

from app.api.deps import get_db
from app.models.user_preference import UserSearchPreference
from app.schemas.user_preference import UserSearchPreferenceCreate, UserSearchPreferenceRead, UserSearchPreferenceUpdate

router = APIRouter()

@router.get("/user/{id}", response_model=list[UserSearchPreferenceRead], status_code=status.HTTP_200_OK)
async def get_user_preference(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    query = select(UserSearchPreference).where(UserSearchPreference.user_id == id)
    
    results = await db.execute(query)
    preferences = results.scalars().all()
    
    return preferences
    

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
    await db.commit()
    
    await db.refresh(db_preference)
    
    return db_preference


@router.patch("/{preference_id}", response_model=UserSearchPreferenceRead)
async def update_user_preference(
    preference_id: int,
    preference_update: UserSearchPreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    # get preference by id
    query = select(UserSearchPreference).where(UserSearchPreference.id == preference_id)
    result = await db.execute(query)
    db_preference = result.scalars().first()
    
    if not db_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find search preference preset with that id"
        )
        
    # update preference data
    update_data = preference_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_preference, field, value)
        
    await db.commit()
    await db.refresh(db_preference)
    
    return db_preference