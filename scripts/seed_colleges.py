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
from dotenv import load_dotenv

COLLEGE_SCORECARD_DATA_URL = "https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_06102026.zip"

SEED_DATA_DIR = os.path.join("database", "seed_data")
LOCAL_CSV_PATH = os.path.join(SEED_DATA_DIR, "Most-Recent-Cohorts-Institution.csv")
TEMP_ZIP_PATH = "temp_scorecard.zip"

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
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

      
def clean_numeric_value(val):
    # Safely convert empty spaces, NaN, or PrivacySuppressed Values to python None
    if pd.isna(val):
        return None
    
    val_str = str(val).strip().lower()
    if val_str in ("privacysuppressed", "null", "nan", "", "none"):
        return None
    
    try:
        float_val = float(val)
        return int(float_val) if float_val.is_integer() else float_val
    except ValueError:
        return None
    

def process_data(file_path):
    # process the csv file with pandas
    
    # data columns in the csv file we want to include
    columns_to_extract = [
        "UNITID", "OPEID", "OPEID6", "INSTNM", "CITY", "STABBR", "ZIP", 
        "ACCREDAGENCY", "INSTURL", "NPCURL", "MAIN", "REGION", "LOCALE", 
        "LATITUDE", "LONGITUDE", "ADM_RATE", "CONTROL",
        "SATVR25", "SATVR75", "SATVRMID", "SATMT25", "SATMT75", "SATMTMID", "SAT_AVG",
        "ACTCM25", "ACTCM75", "ACTCMMID", "UGDS", "TUITIONFEE_IN", "TUITIONFEE_OUT"
    ]
    
    # only read the columns we need
    df = pd.read_csv(file_path, usecols=columns_to_extract, low_memory=False)
    
    # clean up possibly empty values
    df["INSTNM"] = df["INSTNM"].fillna("Unknown School")
    df["CITY"] = df["CITY"].fillna("Unknown City")
    df["STABBR"] = df["STABBR"].fillna("??")
    df["ZIP"] = df["ZIP"].fillna("00000")
    
    # map control numbers to labels in our sql enum
    control_mapping = {1: "public", 2: "private_nonprofit", 3: "private_forprofit"}
    df["school_type"] = df["CONTROL"].map(control_mapping).fillna("public")
    
    cleaned_rows = []
    for _, row in df.iterrows():
        unit_id = clean_numeric_value(row["UNITID"])
        if not unit_id:
            continue
        
        is_main_campus = True if clean_numeric_value(row["MAIN"]) == 1 else False
        
        sat_reading_25 = clean_numeric_value(row["SATVR25"])
        sat_reading_75 = clean_numeric_value(row["SATVR75"])
        sat_reading_50 = clean_numeric_value(row["SATVRMID"])
        
        sat_math_25 = clean_numeric_value(row["SATMT25"])
        sat_math_75 = clean_numeric_value(row["SATMT75"])
        sat_math_50 = clean_numeric_value(row["SATMTMID"])
        
        # Calculate totals dynamically
        sat_total_25 = (sat_reading_25 + sat_math_25) if (sat_reading_25 and sat_math_25) else None
        sat_total_75 = (sat_reading_75 + sat_math_75) if (sat_reading_75 and sat_math_75) else None
        sat_total_50 = (sat_reading_50 + sat_math_50) if (sat_reading_50 and sat_math_50) else None
        
        cleaned_row = (
            unit_id,
            clean_numeric_value(row["OPEID"]),
            clean_numeric_value(row["OPEID6"]),
            str(row["INSTNM"]),
            str(row["CITY"]),
            str(row["STABBR"])[:2],
            str(row["ZIP"])[:20],
            str(row["ACCREDAGENCY"])[:255] if pd.notna(row["ACCREDAGENCY"]) else None,
            str(row["INSTURL"])[:255] if pd.notna(row["INSTURL"]) else None,
            str(row["NPCURL"])[:255] if pd.notna(row["NPCURL"]) else None,
            is_main_campus,
            clean_numeric_value(row["REGION"]),
            clean_numeric_value(row["LOCALE"]),
            clean_numeric_value(row["LATITUDE"]),
            clean_numeric_value(row["LONGITUDE"]),
            clean_numeric_value(row["ADM_RATE"]),
            
            sat_reading_25,
            sat_reading_75,
            sat_reading_50,
            sat_math_25,
            sat_math_75,
            sat_math_50,
            sat_total_25,
            sat_total_75,
            sat_total_50,
            clean_numeric_value(row["SAT_AVG"]),
            
            clean_numeric_value(row["ACTCM25"]),
            clean_numeric_value(row["ACTCM75"]),
            clean_numeric_value(row["ACTCMMID"]),
            
            clean_numeric_value(row["UGDS"]),
            None, # Graduate size (seeded as NULL)
            clean_numeric_value(row["TUITIONFEE_IN"]),
            clean_numeric_value(row["TUITIONFEE_OUT"]),
            row["school_type"],
            None, # Street address (seeded as NULL)
            None  # Median earnings (seeded as NULL)
        )
        cleaned_rows.append(cleaned_row)
        
    print(f"Structured {len(cleaned_rows)} records successfully!")
    return cleaned_rows


def seed_database(records):
    # Insert the processed records into PostgreSQL
    print("Accessing PostgreSQL Database...")
    
    try:
        conn = psycopg2.connect(
            host=DB_BIND_ADDRESS,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO colleges (
                unit_id, opeid, opeid6, name, city, state, zip, 
                accreditation_agency, institution_url, net_price_calculator_url, 
                is_main_campus, region, locale, latitude, longitude, admissions_rate, 
                sat_reading_25th, sat_reading_75th, sat_reading_50th, 
                sat_math_25th, sat_math_75th, sat_math_50th, 
                sat_total_25th, sat_total_75th, sat_total_50th, sat_avg, 
                act_25th, act_75th, act_50th, 
                undergrad_size, graduate_size, in_state_tuition, out_of_state_tuition, 
                school_type, address, median_earnings_9yrs
            ) VALUES %s
            ON CONFLICT (unit_id) DO UPDATE SET
                opeid = EXCLUDED.opeid,
                opeid6 = EXCLUDED.opeid6,
                name = EXCLUDED.name,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                zip = EXCLUDED.zip,
                accreditation_agency = EXCLUDED.accreditation_agency,
                institution_url = EXCLUDED.institution_url,
                net_price_calculator_url = EXCLUDED.net_price_calculator_url,
                is_main_campus = EXCLUDED.is_main_campus,
                region = EXCLUDED.region,
                locale = EXCLUDED.locale,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                admissions_rate = EXCLUDED.admissions_rate,
                sat_reading_25th = EXCLUDED.sat_reading_25th,
                sat_reading_75th = EXCLUDED.sat_reading_75th,
                sat_reading_50th = EXCLUDED.sat_reading_50th,
                sat_math_25th = EXCLUDED.sat_math_25th,
                sat_math_75th = EXCLUDED.sat_math_75th,
                sat_math_50th = EXCLUDED.sat_math_50th,
                sat_total_25th = EXCLUDED.sat_total_25th,
                sat_total_75th = EXCLUDED.sat_total_75th,
                sat_total_50th = EXCLUDED.sat_total_50th,
                sat_avg = EXCLUDED.sat_avg,
                act_25th = EXCLUDED.act_25th,
                act_75th = EXCLUDED.act_75th,
                act_50th = EXCLUDED.act_50th,
                undergrad_size = EXCLUDED.undergrad_size,
                in_state_tuition = EXCLUDED.in_state_tuition,
                out_of_state_tuition = EXCLUDED.out_of_state_tuition,
                school_type = EXCLUDED.school_type;
        """
        
        print(f"Running upsert transaction...")
        execute_values(cursor, insert_query, records)
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM colleges;")
        count = cursor.fetchone()[0]
        print(f"Seeding complete. Database now contains {count} colleges")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")
        sys.exit(1)
        

if __name__ == "__main__":
    download_needed = should_download(COLLEGE_SCORECARD_DATA_URL, LOCAL_CSV_PATH)
    
    if download_needed:
        try:
            # Download zip file
            download_data(COLLEGE_SCORECARD_DATA_URL, TEMP_ZIP_PATH)
            
            # extract csv
            extract_csv_from_zip(TEMP_ZIP_PATH, LOCAL_CSV_PATH)
        finally:
            # Clean up zip after extracting csv
            if os.path.exists(TEMP_ZIP_PATH):
                print("Cleaning up temporary zip file...")
                os.remove(TEMP_ZIP_PATH)
                
    # Seed using csv file no matter if we needed to download or not
    if os.path.exists(LOCAL_CSV_PATH):
        cleaned_records = process_data(LOCAL_CSV_PATH)
        seed_database(cleaned_records)
    else:
        print("Critical Error: Local CSV file is missing. Seed aborted.")
        