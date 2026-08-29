import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PlayerRead(BaseModel):
    id: uuid.UUID
    program_uuid: uuid.UUID | None = None
    clippd_id: str | None = None
    name: str
    rank: int | None = None
    
    scoring_avg: float | None = None
    adjusted_scoring_avg: float | None = None
    top3_finishes: int | None = None
    total_rounds: int | None = None
    win_loss_tie: str | None = None
    wins: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)