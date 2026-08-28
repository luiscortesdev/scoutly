from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, DateTime, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import DivisionType, UserRoleType, SchoolTypeEnum, ClimateType, AcademicRigorType

if TYPE_CHECKING:
    from app.models.user import User

class UserSearchPreference(Base):
    __tablename__ = "user_search_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    divisions: Mapped[list[DivisionType]] = mapped_column(
        ARRAY(SQLEnum(DivisionType, name="division_type", create_type=False)),
        nullable=False
    )
    user_role_desire: Mapped[UserRoleType] = mapped_column(
        SQLEnum(UserRoleType, name="user_role_type", create_type=False),
        nullable=False
    )
    school_type: Mapped[SchoolTypeEnum] = mapped_column(
        SQLEnum(SchoolTypeEnum, name="school_type_enum", create_type=False),
        nullable=False
    )
    climate: Mapped[ClimateType] = mapped_column(
        SQLEnum(ClimateType, name="climate_type", create_type=False),
        nullable=False
    )
    academic_rigor: Mapped[AcademicRigorType] = mapped_column(
        SQLEnum(AcademicRigorType, name="academic_rigor_type", create_type=False), 
        nullable=False
    )

    program_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    min_act: Mapped[int] = mapped_column(Integer, nullable=False)
    min_sat: Mapped[int] = mapped_column(Integer, nullable=False)
    user_test_score_tolerance: Mapped[int] = mapped_column(Integer, nullable=False)
    max_distance: Mapped[int] = mapped_column(Integer, nullable=False)

    preferred_regions: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), 
        nullable=False
    )
    school_size: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), 
        nullable=False
    )
    school_setting: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), 
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # points to preferences attribute on User model
    user: Mapped[User] = relationship("User", back_populates="preferences")