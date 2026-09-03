from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.college import College
from app.schemas.college import CollegeReadWithProgram

router = APIRouter()

@router.get("/{college_id}", response_model=CollegeReadWithProgram)
async def get_college_details(
    college_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(College)
        .where(college_id == College.unit_id)
        .options(
            selectinload(College.programs)
        )
    )
    
    results = await db.execute(query)
    college = results.scalars().first()
    
    if not college:
        raise HTTPException(status_code=404, detail="College id not found!")
    
    return college