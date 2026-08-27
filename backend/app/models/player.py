from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.program import Program

class Player(Base):
    __tablename__ = "players"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    program_uuid: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=True
    )
    clippd_id: Mapped[str | None] = mapped_column(
        String(50), 
        unique=True, 
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
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

    # points to "players" attribute on program model
    program: Mapped[Program] = relationship("Program", back_populates="players")