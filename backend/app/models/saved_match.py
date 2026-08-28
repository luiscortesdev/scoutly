from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Text, DateTime, func, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RecruitingTierType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.program import Program

class SavedMatch(Base):
    __tablename__ = "saved_matches"

    __table_args__ = (
        UniqueConstraint("user_id", "program_id", name="unique_user_program"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("programs.id", ondelete="CASCADE"), 
        nullable=False
    )

    tier: Mapped[RecruitingTierType] = mapped_column(
        SQLEnum(RecruitingTierType, name="recruiting_tier_type", create_type=False),
        nullable=False,
        server_default="undecided",
        default=RecruitingTierType.undecided
    )
    
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # points to saved_matches field in User model
    user: Mapped[User] = relationship("User", back_populates="saved_matches")
    
    # reference programs table for our program field. this relationship is one way
    program: Mapped[Program] = relationship("Program")