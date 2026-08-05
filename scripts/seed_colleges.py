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
    
    
def download_data(url, output_path):
    # Download the zip file in a chunks
    print(f"Initiating stream download of College Scoreboard ZIP...")
    
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Connection to {url} failed. Status: {response.status_code}. Exiting...")
        sys.exit(1)
        
    total_size = int(response.headers.get("content-length", 0))
    bytes_written = 0
    
    with open(output_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024): # 1MB Chunks
            if chunk:
                file.write(chunk)
                bytes_written += len(chunk)
                if total_size > 0:
                    percent = (bytes_written / total_size) * 100
                    print(f"Download Progress: {percent:.2f}% ({bytes_written / (1024*1024):.1f} MB)", end="\r")
                    
    print("\n ZIP download complete!")
    
    
def extract_csv_from_zip(zip_path, target_csv_path):
    # Extracts the csv from the zip file and saves it locally
    print(f"Extracting CSV from {zip_path}...")
    
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]
        if not csv_files:
            print("Error: No csv file found inside the downloaded ZIP.")
            sys.exit(1)
            
        source_csv = csv_files[0]
        print(f"Found target data file: {source_csv}")
        
        with zip_ref.open(source_csv) as source, open(target_csv_path, "wb") as target:
            shutil.copyfileobj(source, target)
            
        print(f"Saved local copy of csv to {target_csv_path}")
        
