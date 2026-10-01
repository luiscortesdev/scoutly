### Skill 3: PostgreSQL 15 & SQLAlchemy 2.0 Async ORM Modeling
**Target:** `backend/app/models/`, database relationships, ENUM definitions.

# SKILL: scoutly-sqlalchemy-async-orm

## Context
PostgreSQL 15 running in Docker via `asyncpg`. Database schema uses strict 3NF with custom PostgreSQL ENUMs and ARRAY columns.

## Rules for Agents
1. Centralized Declarative Base:
   - NEVER instantiate `DeclarativeBase` inside model files. Always import `Base` from `app.db.base`.
2. PostgreSQL Custom ENUMs:
   - Always import Python `StrEnum` classes from `app.models.enums`.
   - When mapping ENUMs in SQLAlchemy columns, ALWAYS pass `create_type=False` to prevent duplicate creation errors:
     `gender: Mapped[GenderType] = mapped_column(SQLEnum(GenderType, name="gender_type", create_type=False), nullable=False)`
3. PostgreSQL Arrays:
   - Map arrays using `sqlalchemy.dialects.postgresql.ARRAY`:
     - Array of Integers: `preferred_regions: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)`
     - Array of Enums: `divisions: Mapped[list[DivisionType]] = mapped_column(ARRAY(SQLEnum(DivisionType, name="division_type", create_type=False)), nullable=False)`
4. Runtime Model Registration:
   - Every single SQLAlchemy model MUST be imported inside `backend/app/models/__init__.py`.
   - `backend/app/main.py` MUST contain `from app import models` to populate SQLAlchemy's class registry at startup.
5. Bidirectional Handshakes:
   - Ensure `back_populates` matches the exact attribute name on the target class (singular for 1-to-1 / many-to-1, plural for 1-to-many).