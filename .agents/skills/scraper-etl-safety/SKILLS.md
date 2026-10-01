---
name: scraper-etl-safety
description: Guidelines for asynchronously inserting data into the postgres database safely
---

# SKILL: scoutly-scraper-etl-safety

## Rules for Agents
1. Database Concurrency & Thread Safety:
   - Multithreaded crawlers MUST use `psycopg2.pool.ThreadedConnectionPool`.
   - Every worker thread MUST acquire and release its own connection via `try...finally: pool.putconn(conn)`.
   - In-memory dictionary updates across threads MUST be guarded with `threading.Lock()`.
2. Atomic Entity Ingestion:
   - Use atomic "Delete-and-Reload" patterns for sub-entities with dynamic event dates:
     `DELETE FROM program_events WHERE program_uuid = %s;` followed by `execute_values()`.
3. Entity Resolution:
   - Resolving scraped entities against DOE colleges MUST follow the 3-tier resolution engine:
     1. Manual JSON override check (`scraper/maps/clippd_to_doe_name.json`).
     2. Exact case-insensitive match (`ILIKE`).
     3. Trigram similarity (`similarity()`) with dynamic thresholding (0.35 for substrings, 0.50 for standard).