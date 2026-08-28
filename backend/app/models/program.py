from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.enums import GenderType, DivisionType

if TYPE_CHECKING:
    from app.models.college import College
    from app.models.player import Player
    from backend.app.models.program_event import ProgramEvent

class Program(Base):
    __tablename__ = "programs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    college_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("colleges.unit_id", ondelete="CASCADE"), 
        nullable=False
    )
    clippd_id: Mapped[str | None] = mapped_column(
        String(50), 
        unique=True, 
        nullable=True
    )

    gender: Mapped[GenderType] = mapped_column(
        SQLEnum(GenderType, name="gender_type", create_type=False),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    conference: Mapped[str | None] = mapped_column(String(255))
    division: Mapped[DivisionType | None] = mapped_column(
        SQLEnum(DivisionType, name="division_type", create_type=False)
    )
    head_coach: Mapped[str | None] = mapped_column(String(255))
    rank: Mapped[int | None] = mapped_column(Integer)
    
    scoring_avg: Mapped[float | None] = mapped_column(Numeric(18, 13))
    adjusted_scoring_avg: Mapped[float | None] = mapped_column(Numeric(18, 13))
    
    top3_finishes: Mapped[int | None] = mapped_column(Integer)
    total_rounds: Mapped[int | None] = mapped_column(Integer)
    win_loss_tie: Mapped[str | None] = mapped_column(String(255))
    wins: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # points to "programs" attribute in college model
    college: Mapped[College] = relationship("College", back_populates="programs")
    
    # points to "program" attribute in player model
    players: Mapped[list[Player]] = relationship("Player", back_populates="program")
    
    # points to "program" attribute in ProgramEvent model
    events: Mapped[list[ProgramEvent]] = relationship("ProgramEvent", back_populates="program")