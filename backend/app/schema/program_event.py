import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class ProgramEventRead(BaseModel):
    id: int
    program_uuid: uuid.UUID | None = None
    name: str
    position: str | None = None
    field_size: str | None = None
    score: str | None = None
    
    event_sg: float
    total_points: float
    weighted_points: float
    total_rounds: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)