from sqlalchemy import String, Integer, Numeric, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Program(Base):
    __tablename__ = "programs"
    
    name: Mapped[str | None] = mapped_column(String(255))
    conference: Mapped[str | None] = mapped_column(String(255))
    head_coach: Mapped[str | None] = mapped_column(String(255))
    rank: Mapped[int | None] = mapped_column(Integer)