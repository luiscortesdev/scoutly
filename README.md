# Scoutly
A free to use and simple way to find the perfect college golf program for you!

# Database
Spin up the database using `docker compose up -d`

Apply the schema using these commands (${} represent your environment variables):
```
docker cp database/schema.sql scoutly_postgres_db:/schema.sql
docker exec -it scoutly_postgres_db psql -U ${DB_USER} -d scoutly -f /schema.sql  
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
