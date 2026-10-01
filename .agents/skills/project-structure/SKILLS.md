---
name: project-structure
description: An overview of the project structure and architecture
---

# SKILL: scoutly-project-structure

## Context & Architecture
Scoutly is a multi-package Python monorepo managed exclusively via `uv` workspaces.
- Root directory (`scoutly/`): Virtual root containing `pyproject.toml` (with `package = false`), shared `uv.lock`, and `.env.docker`.
- Member packages:
  - `backend/`: FastAPI REST API service
  - `scraper/`: Clippd Playwright scrapers and crawlers
  - `scripts/`: Data ingestion & ETL utilities (DOE College Scorecard)
  - `database/`: Database schema and seed data

## Rules for Agents
1. NEVER use `pip install`, `pipenv`, or `poetry`. Always use `uv`.
2. NEVER activate manual virtual environments. Run all commands through `uv run`.
3. When adding dependencies, ALWAYS specify the target package:
   - Bad: `pip install fastapi`
   - Good: `uv add --package backend fastapi`
   - Good: `uv add --package scraper playwright`
   - Good: `uv add --package scripts pandas`
4. Root tasks MUST be executed via workspace commands:
   - Start API: `uv run uvicorn backend.app.main:app --reload`
   - Run Scrapers: `uv run scrape-rankings` / `uv run scrape-details`
   - Seed Colleges: `uv run seed-colleges`
5. Root `.env.docker` is exclusively for Docker Compose container configs. `backend/.env` is strictly for API runtime secrets. NEVER merge or cross-contaminate these files.