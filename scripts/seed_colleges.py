import os
import sys
import shutil
import zipfile
import requests
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

COLLEGE_SCORECARD_DATA_URL = "https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_06102026.zip"

SEED_DATA_DIR = os.path.join("database", "seed_data")
LOCAL_CSV_PATH = os.path.join(SEED_DATA_DIR, "Most-Recent-Cohorts-Institution.csv")
TEMP_ZIP_PATH = "temp_scorecard.zip"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

os.makedirs(SEED_DATA_DIR, exist_ok=True)