# SKILL: fastapi-project-structure

## Rules for Agents
1. Router Aggregator Pattern:
   - Do not mount individual routers directly in `main.py`. Mount them inside `app/api/v1/api.py`, which is then mounted onto `main.py` under the `/api/v1` prefix.
2. Absolute Settings Pathing:
   - In `app/core/config.py`, NEVER use relative `.env` paths. Always anchor dynamically:
     ```python
     BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
     ENV_FILE_PATH = BACKEND_DIR / ".env"
     ```
3. Dependency Injection:
   - Always inject database sessions using `db: AsyncSession = Depends(get_db)`.
4. STRICT EAGER LOADING (Preventing N+1 Queries & Async Greenlet Errors):
   - In async FastAPI, default lazy loading crashes with `MissingGreenlet`.
   - NEVER access relational attributes without explicit loading strategies in `.options()`:
     - For 1-to-1 or Many-to-1 relationships (e.g., `Program.college`): Use `joinedload()` (SQL JOIN).
     - For 1-to-Many lists (e.g., `Program.players`, `Program.events`): Use `selectinload()` (Batch IN clause to avoid Cartesian products).