# Scoutly
A free to use and simple way to find the perfect college golf program for you!

# Database
Spin up the database using `docker compose up -d`

Apply the schema using these commands on windows powershell:
```
Get-Content database/schema.sql | docker exec -i scoutly_postgres_db psql -U scoutly_admin -d scoutly
```

# Scripts
Create a virtual environment using python
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install required python packages
```bash
pip install --upgrade pip
pip install -r scripts/requirements.txt
```

Seed College Scorecard Data
```bash 
python scripts/seed_colleges.py
```

Seed Clippd Rankings Data
```bash
python scraper/scrape_rankings.py
```
NOTE: it is completely normal to see errors for player ids being unable to resolve. These players belong to teams whose college golf programs are no longer ranked/no longer exist. However, Clippd has not removed them from their player rankings.

# Algorithms
The matching algorithm normalizes junior golf tournament performance into a standardized baseline compatible with the collegiate Scoreboard powered by Clippd database. Instead of relying on raw scores or inaccessible USGA course ratings, the algorithm loops through a junior’s round history and applies a specific, tiered "Level of Play" modifier (+1.5 for National, +3.0 for Regional, and +4.5 for Local events. These may be changed with more backtesting.) to each individual round to account for varying course difficulties, pin setups, and field pressures. The algorithm then sorts these adjusted rounds, filters out the worst 25% of scores to eliminate outlier blowout days, and averages the remaining data to generate a clean "App Index" representing the player's true collegiate capability. This final index can be queried directly against a college player's Clippd Adjusted Scoring Average, allowing the platform to seamlessly map junior recruits to optimal, data-backed college roster spots.