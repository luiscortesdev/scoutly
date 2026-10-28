---
name: fastapi-endpoints
description: Conventions for the FastAPI backend in backend/app — routers, settings, DB session injection, async eager loading, and response models. Use when adding or changing API endpoints, writing queries in route handlers, or touching backend/app/api or backend/app/core.
---

# SKILL: fastapi-endpoints

## Context
- FastAPI + SQLAlchemy 2.0 async (`asyncpg`). App entrypoint: `backend/app/main.py`, imported as `app.main:app`.
- The `app` package is only importable from inside `backend/`. Run the API with:
  `cd backend && uv run fastapi dev` (the entrypoint is set in `backend/pyproject.toml` under `[tool.fastapi]`).
- There is no authentication yet (roadmap Phase 4). Endpoints that act on a user take `user_id` explicitly. Do not invent a `current_user` dependency unless the task is to build auth.

## Rules for Agents
1. Router Aggregator Pattern:
   - One module per resource in `app/api/v1/<resource>.py`, each exposing `router = APIRouter()`.
   - Register routers ONLY in `app/api/v1/api.py` (`api_router.include_router(..., prefix="/<resource>", tags=["<resource>"])`). `main.py` mounts `api_router` once under `settings.API_V1_STR` (`/api/v1`). Never mount resource routers in `main.py`.
2. Settings:
   - Read configuration from `app.core.config.settings`. Never call `os.getenv` in the backend.
   - `config.py` anchors the env file to the backend directory so it loads no matter where the process starts:
     ```python
     BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
     ENV_FILE_PATH = BACKEND_DIR / ".env"
     ```
     Never switch it back to a relative `".env"`.
3. Dependency Injection:
   - Inject sessions with `db: AsyncSession = Depends(get_db)` from `app.api.deps`.
4. STRICT EAGER LOADING (prevents N+1 queries and `MissingGreenlet` errors):
   - Async sessions cannot lazy-load. Any relationship serialized by the response model MUST be loaded via `.options()`:
     - Many-to-1 / 1-to-1 (e.g. `Program.college`): `joinedload()`.
     - 1-to-many lists (e.g. `Program.players`, `Program.events`, `College.programs`): `selectinload()` (avoids Cartesian row explosion).
5. Responses & Errors:
   - Always set `response_model=` to a schema from `app/schemas/` and return ORM objects (read schemas use `from_attributes`).
   - Use `fastapi.status` constants for status codes, and `HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=...)` for missing rows.
6. Mutations:
   - Create: build the ORM object from `payload.model_dump()`, `db.add()`, `await db.commit()`, `await db.refresh(obj)`.
   - PATCH: apply `payload.model_dump(exclude_unset=True)` with `setattr`, then commit and refresh.
7. Business Logic Placement:
   - Matching, scoring, and App Index calculations belong in `app/services/` (create it with the first service) as plain functions that can be unit-tested without HTTP. Route handlers stay thin: validate, call the service, return.
