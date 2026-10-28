---
name: scraper-etl-safety
description: Rules for the synchronous psycopg2 ETL code in scraper/ and scripts/ — run order, threaded DB access, idempotent upserts, caching, and resolving Clippd school names to DOE colleges. Use when editing scrape_rankings.py, scrape_details.py, seed_colleges.py, clippd_to_doe_name.json, or writing a new ingestion job.
---

# SKILL: scraper-etl-safety

## Context
- `scripts/` (`seed-colleges`): downloads the DOE College Scorecard zip, cleans it with pandas, merges `database/seed_data/canadian_colleges.csv`, and upserts `colleges`.
- `scraper/` (`scrape-rankings`, `scrape-details`): reads the Clippd Scoreboard JSON API with `requests`, and program pages with `requests` + BeautifulSoup. There is no Playwright.
- Both use synchronous `psycopg2` (not the backend's async stack) and read DB credentials (`DB_*`) from the root `.env` through `python-dotenv`.
- File paths (`scraper/.cache`, `scraper/maps`, `database/.cache`) are relative to the repo root, so jobs MUST be run from the repo root with `uv run <command>`.

## Rules for Agents
1. Run Order (foreign keys depend on it): `seed-colleges` -> `scrape-rankings` -> `scrape-details`.
2. Database Concurrency & Thread Safety:
   - Multithreaded crawlers MUST use `psycopg2.pool.ThreadedConnectionPool`.
   - Every worker acquires and releases its own connection via `try ... finally: pool.putconn(conn)`, and commits or rolls back its own transaction.
   - Shared in-memory caches across threads MUST be guarded with `threading.Lock()`.
3. Idempotent Writes (jobs are re-run regularly):
   - Top-level entities upsert on their natural key with `INSERT ... ON CONFLICT (<key>) DO UPDATE`: `colleges.unit_id`, `programs.clippd_id`, `players.clippd_id`.
   - Sub-entities without a stable key use an atomic delete-and-reload in one transaction:
     `DELETE FROM program_events WHERE program_uuid = %s;` followed by `execute_values()`.
   - Use `execute_values()` for bulk inserts, never row-by-row `execute()` in a loop.
4. Entity Resolution (Clippd school name -> DOE `colleges.unit_id`), implemented in `resolve_college_id`:
   1. Manual map `scraper/maps/clippd_to_doe_name.json`: an `int` value is a direct `unit_id` override; a `str` value is the DOE name used in the next steps.
   2. Exact case-insensitive match (`name ILIKE %s`).
   3. Trigram fuzzy match (`pg_trgm`, enabled by `scrape-rankings`): candidates come from `name % <lookup> OR name ILIKE '%<lookup>%'`, and the best one is accepted only if `similarity() > 0.5`.
   - Unresolved schools are logged and skipped. Fix wrong or missing matches by adding a map entry, NOT by lowering the threshold.
5. Caching & Politeness:
   - Respect the local caches (`scraper/.cache/*.json`, 1-week TTL for rankings; `database/.cache` for the Scorecard CSV). Don't add code paths that bypass them by default.
   - Network calls go through the retry/backoff helper with timeouts. Keep the request delays, and don't raise `max_threads` (15) without a reason.
6. Ownership: ETL jobs write only to `colleges`, `programs`, `players`, `program_events`. Never write to user tables.
