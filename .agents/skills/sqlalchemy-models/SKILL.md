---
name: sqlalchemy-models
description: Conventions for SQLAlchemy 2.0 async ORM models on PostgreSQL 17 in backend/app/models — declarative base, Postgres ENUMs and ARRAYs, relationships, and keeping models in sync with database/schema.sql. Use when creating or editing models, relationships, enums, or table columns.
---

# SKILL: sqlalchemy-models

## Context
- PostgreSQL 17 runs in Docker; the backend reaches it through `asyncpg`.
- `database/schema.sql` is the source of truth for the schema. There are no migrations yet (Alembic is a roadmap item), and the ORM never creates tables or types.

## Rules for Agents
1. Schema Changes Touch Both Sides:
   - Any column, table, or enum change goes into `database/schema.sql` AND the matching model in `backend/app/models/` (plus `app.models.enums` for enums) in the same change.
2. Centralized Declarative Base:
   - Never subclass `DeclarativeBase` in model files. Always `from app.models.base import Base`.
3. PostgreSQL Custom ENUMs:
   - Define a Python `StrEnum` in `app.models.enums` whose values match the SQL enum exactly.
   - Always pass `create_type=False` (the type is created by `schema.sql`):
     `gender: Mapped[GenderType] = mapped_column(SQLEnum(GenderType, name="gender_type", create_type=False), nullable=False)`
4. PostgreSQL Arrays (`sqlalchemy.dialects.postgresql.ARRAY`):
   - Integers: `preferred_regions: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)`
   - Enums: `divisions: Mapped[list[DivisionType]] = mapped_column(ARRAY(SQLEnum(DivisionType, name="division_type", create_type=False)), nullable=False)`
5. Runtime Model Registration:
   - Every model MUST be imported in `backend/app/models/__init__.py`.
   - `backend/app/main.py` keeps `from app import models` so the registry is populated before relationships are configured.
6. Relationships:
   - Type relationships with `TYPE_CHECKING` imports and unquoted annotations, with no `from __future__` import (see `python-typing-standards`):
     `players: Mapped[list[Player]] = relationship("Player", back_populates="program")`
   - `back_populates` must name the exact attribute on the other class. Use a singular name for many-to-1 / 1-to-1 and a plural one for 1-to-many, and make the `Mapped[...]` type (and `uselist`) match the real cardinality in `schema.sql`.
7. Types:
   - `NUMERIC` columns are annotated `float`, but asyncpg returns `Decimal`; Pydantic read schemas coerce them to `float`. Keep that in mind when doing arithmetic in services.
   - UUID primary keys: `UUID(as_uuid=True), primary_key=True, default=uuid.uuid4`. Timestamps: `DateTime(timezone=True), server_default=func.now()`.
