import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from app.models.enums import GenderType, DivisionType

from app.schemas.program_event import ProgramEventRead
from app.schemas.player import PlayerRead

if TYPE_CHECKING:
    from app.schemas.college import CollegeRead

# our frontend will only read programs
class ProgramRead(BaseModel):
    id: uuid.UUID
    college_id: int
    clippd_id: str | None = None # assign default value of None
    gender: GenderType
    name: str
    conference: str | None = None
    division: DivisionType | None = None
    head_coach: str | None = None
    rank: int | None = None
    
    scoring_avg: float | None = None
    adjusted_scoring_avg: float | None = None
    top3_finishes: int | None = None
    total_rounds: int | None = None
    win_loss_tie: str | None = None
    wins: int | None = None
    
    created_at: datetime
    
    # allow pydantic to read from orm models
    model_config = ConfigDict(from_attributes=True)
    
class ProgramReadDetailed(ProgramRead):
    college: "CollegeRead"
    events: list[ProgramEventRead] = []
    players: list[PlayerRead] = []
    
# fix circular imports between college and program schemas
from app.schemas.college import CollegeRead
ProgramReadDetailed.model_rebuild()