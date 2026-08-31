from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
import uuid

from app.api.deps import get_db
from app.models.program import Program
from app.schemas.program import ProgramReadDetailed

router = APIRouter()

@router.get("/{program_id}", response_model=ProgramReadDetailed)
async def get_program_details(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Program)
        .where(program_id == Program.id)
        .options(
            joinedload(Program.college),
            selectinload(Program.events),
            selectinload(Program.players)
        )
    )
    
    results = await db.execute(query)
    program = results.scalars().first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program id not found!")
    
    return program
        