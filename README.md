# Scoutly
An AI-powered college golf recruiting counselor.

Scoutly matches high school golfers with college golf programs by combining athletic data from the [Clippd Scoreboard](https://scoreboard.clippd.com/), academic data from the U.S. Department of Education [College Scorecard](https://collegescorecard.ed.gov/), and each player's own preferences. See the [roadmap](docs/roadmap.md) for project status and what's planned next.

# Project Structure
This is a Python monorepo managed with [uv](https://docs.astral.sh/uv/) workspaces.

| Path | Description |
| :--- | :--- |
| `backend/` | FastAPI REST API (SQLAlchemy 2.0 async + Pydantic v2) |
| `scraper/` | Clippd rankings and details scrapers |
| `scripts/` | DOE College Scorecard seeding |
| `database/` | PostgreSQL schema and seed data |
| `docs/` | Roadmap and design docs |

# Setup
The following instructions assume that you have [uv](https://docs.astral.sh/uv/) and Docker installed on your machine.

## Environment Variables
Create a `.env` file in the repo root. It is used by Docker Compose, the scraper, and the scripts:
```bash
DB_USER=scoutly_admin
DB_PASSWORD=<choose a password>
DB_BIND_ADDRESS=127.0.0.1
DB_PORT=5432
```

Create a `backend/.env` file for the API with the same credentials:
```bash
POSTGRES_USER=scoutly_admin
POSTGRES_PASSWORD=<same password>
```

## Database
Spin up the database using `docker compose up -d`

Apply the schema using this command in Windows PowerShell (replace `scoutly_admin` if you chose a different `DB_USER`):
```powershell
Get-Content database/schema.sql | docker exec -i scoutly_postgres_db psql -U scoutly_admin -d scoutly
```

# Scripts
Make sure your Postgres database is running, and run these commands from the repo root.

First, initialize a virtual environment and install dependencies using uv.
```bash
uv sync
```

Next, we can seed the United States Department of Education [College Scorecard](https://collegescorecard.ed.gov/) data in our database.
```bash
uv run seed-colleges
```

We then seed rankings data from the [Clippd Scoreboard](https://scoreboard.clippd.com/) API.
```bash
uv run scrape-rankings
```
NOTE: it is completely normal to see errors for player ids being unable to resolve. These players belong to teams whose college golf programs are no longer ranked/no longer exist. However, Clippd has not removed them from their player rankings.

Finally, we can seed Clippd event data and other miscellaneous details.
```bash
uv run scrape-details
```

These steps must run in this order, since programs reference colleges and events reference programs. Responses are cached locally (`scraper/.cache`, `database/.cache`), so re-runs are faster and safe to repeat.

# Running the API
```bash
cd backend
uv run fastapi dev
```
The API is served at http://127.0.0.1:8000, with interactive docs at http://127.0.0.1:8000/docs. All endpoints are under `/api/v1`.

# Algorithms
The matching algorithm normalizes junior golf tournament performance into a standardized baseline compatible with the collegiate Scoreboard powered by Clippd database. Instead of relying on raw scores or inaccessible USGA course ratings, the algorithm loops through a junior's round history and applies a specific, tiered "Level of Play" modifier (+1.5 for National, +3.0 for Regional, and +4.5 for Local events. These may be changed with more backtesting. The modifier for State events is still to be decided.) to each individual round to account for varying course difficulties, pin setups, and field pressures. The algorithm then sorts these adjusted rounds, filters out the worst 25% of scores to eliminate outlier blowout days, and averages the remaining data to generate a clean "App Index" representing the player's true collegiate capability. This final index can be queried directly against a college player's Clippd Adjusted Scoring Average, allowing the platform to seamlessly map junior recruits to optimal, data-backed college roster spots.

The App Index is not implemented yet. It is the next item on the [roadmap](docs/roadmap.md).

# Working with AI Agents
Agent instructions live in [`AGENTS.md`](AGENTS.md), which most AI coding tools read automatically (`CLAUDE.md` simply imports it). Task-specific rules live in [`.agents/skills/`](.agents/skills/) as `SKILL.md` files. If you change a convention in the code, update the matching skill in the same PR.
