# AGENTS.md

Instructions for AI coding agents (Codex, Cursor, Copilot, Claude Code, Gemini CLI, …) working in this repo. Humans should start with [README.md](README.md).

## Project
Scoutly matches high school golfers with college golf programs using athletic data (Clippd Scoreboard), academic data (DOE College Scorecard), and user preferences.
Status, phases, design decisions, and open questions: **[docs/roadmap.md](docs/roadmap.md)**. Read it before planning a feature, and update its status markers when you finish one.

## Repo map
Python monorepo managed with **uv workspaces** (root `pyproject.toml` has `package = false`; one shared `uv.lock`).

| Path | What it is |
| :--- | :--- |
| `backend/` | FastAPI REST API. Package `app` (`app/api/v1`, `app/core`, `app/db`, `app/models`, `app/schemas`). |
| `scraper/` | Clippd ingestion: `scrape_rankings.py` (JSON API), `scrape_details.py` (HTML + BeautifulSoup, threaded). `maps/clippd_to_doe_name.json` holds manual name overrides. |
| `scripts/` | `seed_colleges.py`: DOE College Scorecard download and seed. |
| `database/` | `schema.sql` (source of truth for the schema) and `seed_data/`. |
| `docs/` | Roadmap and design docs. |
| `.agents/skills/` | Task-specific agent instructions (see below). |

There is no frontend yet (planned: Next.js, see the roadmap).

## Commands
Run everything through `uv`, from the repo root unless noted.

```bash
uv sync                                   # install all workspace packages
docker compose up -d                      # start Postgres 17 (container: scoutly_postgres_db)
uv run seed-colleges                      # 1. DOE colleges
uv run scrape-rankings                    # 2. Clippd programs + players
uv run scrape-details                     # 3. Clippd program details + events
cd backend && uv run fastapi dev          # API with reload on http://127.0.0.1:8000 (docs at /docs)
```

Apply the schema to a fresh database (PowerShell):
```powershell
Get-Content database/schema.sql | docker exec -i scoutly_postgres_db psql -U <DB_USER> -d scoutly
```

There is no test suite, linter config, or CI yet. To check backend changes, at minimum import the app and configure the mappers:
```bash
cd backend && uv run python -c "from app.main import app; from sqlalchemy.orm import configure_mappers; configure_mappers()"
```

## Environment files
- Root `.env`: `DB_USER`, `DB_PASSWORD`, `DB_BIND_ADDRESS`, `DB_PORT`. Read by `docker-compose.yml` and by the scraper and scripts (via `python-dotenv`).
- `backend/.env`: `POSTGRES_*` settings for the API, loaded by `app/core/config.py`.
- Never commit either file, and never print their values.

## Always-on rules
1. **Use uv only.** Never `pip install`, poetry, or pipenv, and never activate a venv by hand. Add dependencies to the right package: `uv add --package backend <dep>` / `--package scraper` / `--package scripts`.
2. **Python 3.14 typing:** never add `from __future__ import annotations`; use `X | None` and `list[...]`; forward references need no quotes. Backend imports start with `app.` (never `backend.app.`).
3. **Schema changes** go into `database/schema.sql` and the matching SQLAlchemy model in the same change. There are no migrations yet.
4. **Data ownership:** scrapers and seed scripts own `colleges`, `programs`, `players`, `program_events` (read-only in the API). Users own `users`, `user_search_preferences`, `user_events`, `saved_matches`.
5. **Business logic** (matching, App Index, scoring) goes in `backend/app/services/` as plain, testable functions, not in route handlers or the frontend.
6. **$0 cloud budget:** never propose RDS, load balancers, NAT gateways, or other paid infrastructure. Everything runs in Docker on one EC2 instance.
7. **Security:** hash passwords (Argon2id or bcrypt); validate every request body with Pydantic.

## Skills: read the matching file before working in that area
Each skill is a folder with a `SKILL.md` following the open [Agent Skills](https://agentskills.io) format. If your tool doesn't load skills automatically, open the file yourself when the task matches.

| Skill | Read when you are… |
| :--- | :--- |
| [`fastapi-endpoints`](.agents/skills/fastapi-endpoints/SKILL.md) | adding or changing endpoints, queries, or settings in `backend/app/api` or `backend/app/core` |
| [`sqlalchemy-models`](.agents/skills/sqlalchemy-models/SKILL.md) | editing `backend/app/models`, enums, relationships, or `database/schema.sql` |
| [`pydantic-schemas`](.agents/skills/pydantic-schemas/SKILL.md) | editing `backend/app/schemas` or defining request/response shapes |
| [`python-typing-standards`](.agents/skills/python-typing-standards/SKILL.md) | writing type hints or untangling circular imports |
| [`scraper-etl-safety`](.agents/skills/scraper-etl-safety/SKILL.md) | editing anything in `scraper/` or `scripts/`, or writing a new ingestion job |

## Keeping this context accurate
- These files describe the code **as it is**. If you change a convention, update the relevant skill or this file in the same PR. If a rule and the code disagree, raise it instead of silently following either one.
- Planned or aspirational items belong in `docs/roadmap.md`, not in rules.
- New skill: add `.agents/skills/<name>/SKILL.md` with `name: <name>` (must match the folder) and a `description` that says when to use it, then add a row to the table above.
