from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.program import Program 

class Base(DeclarativeBase):
    pass

class College(Base):
    __tablename__ = "colleges"

    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opeid: Mapped[str | None] = mapped_column(String(50))
    opeid6: Mapped[str | None] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(10), nullable=False)  # Maps to CHAR(10)
    zip: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    
    accreditation_agency: Mapped[str | None] = mapped_column(String(255))
    institution_url: Mapped[str | None] = mapped_column(String(255))
    net_price_calculator_url: Mapped[str | None] = mapped_column(String(255))
    is_main_campus: Mapped[bool | None] = mapped_column(Boolean)
    region: Mapped[int | None] = mapped_column(Integer)
    locale: Mapped[int | None] = mapped_column(Integer)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    
    admissions_rate: Mapped[float | None] = mapped_column(Numeric(4, 2))
    
    sat_reading_25th: Mapped[int | None] = mapped_column(Integer)
    sat_reading_75th: Mapped[int | None] = mapped_column(Integer)
    sat_reading_50th: Mapped[int | None] = mapped_column(Integer)
    sat_math_25th: Mapped[int | None] = mapped_column(Integer)
    sat_math_75th: Mapped[int| None] = mapped_column(Integer)
    sat_math_50th: Mapped[int| None] = mapped_column(Integer)
    sat_total_25th: Mapped[int | None] = mapped_column(Integer)
    sat_total_75th: Mapped[int | None] = mapped_column(Integer)
    sat_total_50th: Mapped[int | None] = mapped_column(Integer)
    sat_avg: Mapped[int | None] = mapped_column(Integer)
    
    act_25th: Mapped[int | None] = mapped_column(Integer)
    act_75th: Mapped[int | None] = mapped_column(Integer)
    act_50th: Mapped[int | None] = mapped_column(Integer)
    
    undergrad_size: Mapped[int | None] = mapped_column(Integer)
    graduate_size: Mapped[int | None] = mapped_column(Integer)
    in_state_tuition: Mapped[int | None] = mapped_column(Integer)
    out_of_state_tuition: Mapped[int | None] = mapped_column(Integer)
    school_type: Mapped[str | None] = mapped_column(String(100))
    median_earnings_9yrs: Mapped[int | None] = mapped_column(Integer)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    programs: Mapped[list[Program]] = relationship("Program", back_populates="college")