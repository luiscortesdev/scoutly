# Scoutly
A free to use and simple way to find the perfect college golf program for you!

# Database
Spin up the database using `docker compose up -d`

Apply the schema using this command:
`docker exec -i scoutly_postgres_db psql -U postgres -d scoutly < database/schema.sql`

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
