# Scoutly
An AI-powered college golf recruiting counselor.

# Database
Spin up the database using `docker compose up -d`

Apply the schema using these commands on windows powershell:
```bash
Get-Content database/schema.sql | docker exec -i scoutly_postgres_db psql -U scoutly_admin -d scoutly
```

# Scripts
This project uses [uv](https://docs.astral.sh/uv/) as its package manager. The following instructions assume that you have uv installed on your machine. Additionally, ensure that your Postgres database is active.

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
uv run scrape-rankings
```

# Algorithms
The matching algorithm normalizes junior golf tournament performance into a standardized baseline compatible with the collegiate Scoreboard powered by Clippd database. Instead of relying on raw scores or inaccessible USGA course ratings, the algorithm loops through a junior’s round history and applies a specific, tiered "Level of Play" modifier (+1.5 for National, +3.0 for Regional, and +4.5 for Local events. These may be changed with more backtesting.) to each individual round to account for varying course difficulties, pin setups, and field pressures. The algorithm then sorts these adjusted rounds, filters out the worst 25% of scores to eliminate outlier blowout days, and averages the remaining data to generate a clean "App Index" representing the player's true collegiate capability. This final index can be queried directly against a college player's Clippd Adjusted Scoring Average, allowing the platform to seamlessly map junior recruits to optimal, data-backed college roster spots.