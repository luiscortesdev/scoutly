from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EventLevelType

if TYPE_CHECKING:
    from app.models.user import User

class UserEvent(Base):
    __tablename__ = "user_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_tour_name: Mapped[str | None] = mapped_column(String(255))
    course_name: Mapped[str | None] = mapped_column(String(255))
    
    event_level: Mapped[EventLevelType | None] = mapped_column(
        SQLEnum(EventLevelType, name="event_level_type", create_type=False)
    )
    
    yardage: Mapped[int | None] = mapped_column(Integer)
    scores: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), 
        nullable=False
    )
    par: Mapped[int | None] = mapped_column(Integer)
    finish: Mapped[int | None] = mapped_column(Integer)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # references "events" attribute on User model
    user: Mapped[User] = relationship("User", back_populates="events")