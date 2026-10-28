---
name: pydantic-schemas
description: Conventions for Pydantic v2 request/response schemas in backend/app/schemas — which schema variants to create, ORM mode, validation constraints, and circular references. Use when creating or editing files in backend/app/schemas or defining an endpoint's request/response shape.
---

# SKILL: pydantic-schemas

## Context
Pydantic v2 is used for request validation and response serialization. Schemas mirror the ORM models in `backend/app/models/` and reuse their enums from `app.models.enums`.

## Rules for Agents
1. Read-Only vs. Write-Capable Segregation:
   - Tables filled only by the scrapers and seed scripts (`colleges`, `programs`, `players`, `program_events`) get ONLY `<Model>Read` and, when nested relations are returned, `<Model>ReadDetailed`. Never add `Create`/`Update` schemas for them.
   - User-owned mutable tables (`users`, `user_search_preferences`, `user_events`, `saved_matches`) get the family `<Model>Base`, `<Model>Create`, `<Model>Update`, `<Model>Read`.
   - `Update` schemas make every field optional (`T | None = None`) and are applied with `model_dump(exclude_unset=True)`.
2. ORM Mode:
   - Every `Read` schema declares `model_config = ConfigDict(from_attributes=True)`.
   - Never use the v1 syntax `class Config: orm_mode = True`.
3. Input Validation via `Field` (on `Base`/`Create`, mirrored on `Update`):
   - SAT scores: `Field(ge=400, le=1600)`
   - ACT scores: `Field(ge=1, le=36)`
   - Mandatory multi-select arrays (e.g. `divisions`): `Field(min_length=1)`
4. Circular References (e.g. `CollegeReadDetailed` <-> `ProgramRead`):
   - Import the other schema under `if TYPE_CHECKING:` at the top, annotate normally (no string quotes needed on Python 3.14), then add a bottom-of-file runtime import and call `.model_rebuild()`. Without the rebuild Pydantic raises "`X` is not fully defined". See `python-typing-standards` for the full pattern.
