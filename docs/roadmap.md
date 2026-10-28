# Scoutly Roadmap

Living status document. Update the status markers in the same PR that changes them.
Legend: ✅ done · 🚧 in progress / partial · ⬜ not started

## Mission
Match prospective high school golfers with college golf programs (NCAA D1–D3, NAIA, NJCAA, plus a handful of Canadian schools) based on athletic metrics, academic standing, and personal preferences.

### Key capabilities
- **Athletic fit:** compare a junior's normalized scoring (the App Index, below) against each program's roster of Clippd adjusted scoring averages, and estimate the role the player could earn (best player, travel squad, redshirt, walk-on).
- **Academic fit:** compare the player's GPA and SAT/ACT with DOE College Scorecard admissions percentiles (25th/50th/75th).
- **Preference filters:** division, region, distance, climate, school type and size, setting, program rank, academic rigor.
- **Comparison:** side-by-side program views combining golf performance with academics, cost, and outcomes.

## Architecture

| Layer | Technology | Status |
| :--- | :--- | :--- |
| Database | PostgreSQL 17 (Docker), schema in `database/schema.sql` | ✅ |
| Ingestion | Python, `requests` + BeautifulSoup (Clippd), pandas (DOE Scorecard), `psycopg2` | ✅ |
| Backend API | FastAPI, SQLAlchemy 2.0 async, `asyncpg`, Pydantic v2 | 🚧 |
| Frontend | Next.js (App Router, TS), TailwindCSS, shadcn/ui, TanStack Query | ⬜ planned |
| Hosting | Single AWS EC2 free-tier instance (Docker Compose + Nginx/Certbot); frontend on Vercel | ⬜ planned |

Monorepo layout and commands live in [`AGENTS.md`](../AGENTS.md).

### Decisions log
| Decision | Why |
| :--- | :--- |
| FastAPI over Go | One language across ingestion, API, and the matching algorithm. Async SQLAlchemy covers performance needs. |
| `requests` + Clippd JSON API instead of Playwright | Clippd exposes a JSON rankings API, and its detail pages render server-side, so a headless browser isn't needed. |
| PostgreSQL 17 in Docker on EC2, not RDS | Keeps hosting at $0 (avoids RDS and the public IPv4 charge). |
| DOE `unit_id` as the college primary key | Stable federal identifier; every program resolves to one. |
| Raw `schema.sql`, no ORM-created tables | The schema uses Postgres ENUMs and ARRAYs and is shared by the sync ETL and the async API. Alembic is planned. |
| Python 3.14, no `from __future__ import annotations` | PEP 649 lazy annotations make it unnecessary. |
| Player graduation year not scraped | Needs one request per player, which is too slow. Revisit for roster-opening predictions. |

## Data model (current)
- `colleges` (DOE Scorecard + Canadian seed): identity, location, region/locale codes, admissions rate, SAT/ACT percentiles, size, tuition, earnings.
- `programs` → `colleges`: Clippd team rankings, division, conference, coach, scoring and adjusted scoring averages.
- `players` → `programs`: Clippd individual rankings and adjusted scoring averages.
- `program_events` → `programs`: per-event team results (deleted and reloaded on every scrape).
- `users`: account, demographics, academics (GPA, SAT/ACT), handicap, location.
- `user_search_preferences` → `users`: named preference presets.
- `user_events` → `users`: junior tournament results with per-round `scores[]` and `event_level`.
- `saved_matches` → `users`, `programs`: bookmarked programs with a recruiting tier and notes.
- View `user_scoring_averages`: plain average of all rounds (to be replaced by the App Index).

## Matching algorithm: App Index (design)
Normalize junior tournament scoring onto the same scale as Clippd's collegiate adjusted scoring average:
1. For each round in a user's `user_events.scores`, add a level-of-play modifier: **national +1.5, regional +3.0, local +4.5** (to be tuned by backtesting).
2. Sort the adjusted rounds and drop the worst 25% to remove blowout days.
3. Average the rest → **App Index**.
4. Compare the App Index with `players.adjusted_scoring_avg` on each roster to estimate where the player would slot in (sets athletic fit and likely role).

Overall match score (initial weights): athletic 40%, academic 30%, preferences/financial 30%.

## Phases

### Phase 1: Data engineering & normalization ✅ (mostly)
- ✅ PostgreSQL schema (`database/schema.sql`)
- ✅ DOE College Scorecard ingestion (`uv run seed-colleges`), with Canadian supplement
- ✅ Clippd rankings ingestion for programs and players (`uv run scrape-rankings`)
- ✅ Program detail and event scraping (`uv run scrape-details`)
- ✅ School-name resolution: manual JSON map → `ILIKE` → trigram similarity
- ⬜ Schema migrations (Alembic) instead of applying `schema.sql` by hand

### Phase 2: Core API & matching engine 🚧
- ✅ `GET /api/v1/colleges/{id}` (with programs)
- ✅ `GET /api/v1/programs/{id}` (with college, players, events)
- ✅ CRUD for `/api/v1/preferences`
- ⬜ `GET /api/v1/colleges` and `GET /api/v1/programs` list endpoints with filtering and pagination
- ⬜ App Index service in `backend/app/services/`, with unit tests ← **next up**
- ⬜ `POST /api/v1/match`: accepts a golfer profile and preferences, returns ranked programs with fit breakdowns
- ⬜ CRUD for `user_events` and `saved_matches`

### Phase 3: Frontend ⬜
- Search filters, program cards, match results, score comparison views (shadcn/ui)
- TanStack Query for fetching, caching, and debounced filters
- Side-by-side program comparison page

### Phase 4: Authentication & user profiles ⬜
- Registration and login with `HttpOnly` cookie JWT or session tokens; Argon2id password hashing
- Replace explicit `user_id` parameters with an authenticated user dependency
- Dashboard for academics, handicap, and tournament history; saved matches

### Phase 5: Containerization & deployment ⬜
- 🚧 `docker-compose.yml` (Postgres only so far)
- Dockerfiles for the API and scraper; Nginx reverse proxy with TLS
- Scheduled scraper runs (cron) on EC2; frontend on Vercel

### Phase 6: Hardening ⬜
- Unit and integration tests (matching engine first)
- GitHub Actions CI: lint, format, tests
- README architecture diagram

## Open questions & known issues
- **`state` event level has no App Index modifier.** `event_level_type` includes `state`, but the algorithm only defines national, regional, and local.
- **Preference cardinality mismatch.** `User.preferences` is mapped one-to-one (`uselist=False`), but the table and `GET /preferences/user/{id}` support several named presets per user.
- **No auth.** The preferences endpoints trust a caller-supplied `user_id`.
- `user_scoring_averages` ignores par and level of play.

## Guardrails
- **$0 cloud budget:** no RDS, ALBs, or NAT gateways. Everything runs in Docker on one free-tier EC2 instance.
- **Separation of concerns:** no scoring logic or database access in the frontend. It talks only to typed backend JSON endpoints.
- **Security:** never store plaintext passwords (Argon2id or bcrypt); validate every request body with Pydantic.
- **Accessibility:** UI built on shadcn/ui (Radix) primitives with keyboard and ARIA support.
