from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, Date, DateTime, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import GenderType

if TYPE_CHECKING:
    from app.models.user_preference import UserSearchPreference
    from app.models.user_event import UserEvent
    from app.models.saved_match import SavedMatch

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)

    gender: Mapped[GenderType] = mapped_column(
        SQLEnum(GenderType, name="gender_type", create_type=False),
        nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    graduation_year: Mapped[str | None] = mapped_column(String(4))
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(500), nullable=False)
    zip: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))

    sat_reading: Mapped[int | None] = mapped_column(Integer)
    sat_math: Mapped[int | None] = mapped_column(Integer)
    sat_total: Mapped[int | None] = mapped_column(Integer)
    act_cumulative: Mapped[int | None] = mapped_column(Integer)
    
    gpa_unweighted: Mapped[float | None] = mapped_column(Numeric(3, 2))
    gpa_weighted: Mapped[float | None] = mapped_column(Numeric(3, 2))

    handicap: Mapped[str | None] = mapped_column(String(10))
    home_course: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # points to user attribute on UserSearchPreference model
    preferences: Mapped[UserSearchPreference | None] = relationship(
        "UserSearchPreference", 
        back_populates="user", 
        uselist=False
    )

    # points to user attribute on UserEvent model
    events: Mapped[list[UserEvent]] = relationship("UserEvent", back_populates="user")
    
    # points towards user attribute in SavedMatch model
    saved_matches: Mapped[list[SavedMatch]] = relationship("SavedMatch", back_populates="user")