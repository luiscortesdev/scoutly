# SKILL: scoutly-pydantic-v2-schemas

## Context
Pydantic v2 (Rust core) is used for input validation and JSON serialization.

## Rules for Agents
1. Read-Only vs. Write-Capable Segregation:
   - If a table is managed strictly by scrapers (e.g., `colleges`, `programs`, `players`, `program_events`), DO NOT create `Create` or `Update` schemas. Create ONLY `Read` and `ReadDetailed` schemas.
   - For user-facing mutable tables (`users`, `user_search_preferences`, `user_events`, `saved_matches`), implement the standard family: `Base`, `Create`, `Update`, `Read`.
2. ORM Mode:
   - All `Read` schemas MUST declare: `model_config = ConfigDict(from_attributes=True)`.
   - DO NOT use the legacy v1 syntax: `class Config: orm_mode = True`.
3. Input Validation via `Field`:
   - Enforce domain constraints on incoming payloads:
     - SAT scores: `ge=400, le=1600`
     - ACT scores: `ge=1, le=36`
     - Array minimum lengths: `min_length=1` on mandatory selections (like `divisions`).