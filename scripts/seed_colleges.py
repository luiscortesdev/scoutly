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

def should_download(url, local_path):
    # Check if college scorecard data has been changed
    # since the last time we downloaded (if we have downloaded it before)
    if not os.path.exists(local_path):
        print("Local CSV not found. Proceeding with fresh download...")
        return True
        
    try:
        response = requests.head(url, allow_redirects=True)
        server_last_modified = response.headers.get("Last-Modified") # get when the data was last modified
        
        if not server_last_modified:
            print("Last-Modified header not supported. Defaulting to download...")
            return True
        
        # convert to utc
        server_last_modified_time = parsedate_to_datetime(server_last_modified)
        
        if server_last_modified_time.tzinfo is None:
            server_last_modified_time = server_last_modified.replace(tzinfo=timezone.utc)
        else:
            server_last_modified_time = server_last_modified_time.astimezone(timezone.utc)
        
        
        local_last_modified_time_epoch = os.path.getmtime(local_path) # get when the local csv was last modified
        local_last_modified_time = datetime.fromtimestamp(local_last_modified_time_epoch, tz=timezone.utc) # convert to utc
        
        if server_last_modified_time > local_last_modified_time:
            print(f"New data available! (Last Updated Server: {server_last_modified_time} > Last Updated Locally: {local_last_modified_time}) Downloading...")
            return True
        else:
            print(f"Local data is up to date (Last Updated Locally: {local_last_modified_time} >= Last Updated Server: {server_last_modified_time}). Skipping download...")
            return False
            
    except Exception as e:
        print(f"Error checking updates ({e}). Defaulting to download.")
        return True