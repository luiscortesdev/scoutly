from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.program import Program

class ProgramEvents(Base):
    __tablename__ = "program_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_uuid: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str | None] = mapped_column(String(10))
    field_size: Mapped[str | None] = mapped_column(String(10))
    score: Mapped[str | None] = mapped_column(String(10))

    event_sg: Mapped[float | None] = mapped_column(
        Numeric(6, 3), 
        server_default="0", 
        default=0.0
    )
    total_points: Mapped[float | None] = mapped_column(
        Numeric(6, 3), 
        server_default="0", 
        default=0.0
    )
    weighted_points: Mapped[float | None] = mapped_column(
        Numeric(6, 3), 
        server_default="0", 
        default=0.0
    )
    total_rounds: Mapped[int | None] = mapped_column(Integer)

    start_date: Mapped[date | None] = mapped_column(
        Date, 
        server_default=func.current_date(),
        default=date.today
    )
    end_date: Mapped[date | None] = mapped_column(
        Date, 
        server_default=func.current_date(),
        default=date.today
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # point to events attribute in program model
    program: Mapped[Program] = relationship("Program", back_populates="events")