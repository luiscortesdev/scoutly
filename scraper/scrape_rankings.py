import os
import time
import requests
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

CLIPPD_RANKINGS_API_BASE_URL = "https://scoreboard.clippd.com/api/rankings/leaderboard"
CACHE_DIR = os.path.join("scraper", ".cache")
PROGRAM_CACHE_FILE_PATH = os.path.join(CACHE_DIR, "clippd_program_rankings.json")
PLAYER_CACHE_FILE_PATH = os.path.join(CACHE_DIR, "clippd_player_rankings.json")
CACHE_EXPIRATION_SECONDS = 7 * 24 * 60 * 60 # 1 week

MAPS_DIR = os.path.join("scraper", "maps")
CLIPPD_NAME_TO_DOE_NAME_MAP_PATH = os.path.join(MAPS_DIR, "clippd_to_doe_name.json")
with open(CLIPPD_NAME_TO_DOE_NAME_MAP_PATH, "r") as f:
    MANUAL_PROGRAM_NAME_MAP = json.load(f)

os.makedirs(CACHE_DIR, exist_ok=True)

# helper functions
def map_division(div):
    # map clippd api divisions to our division enum
    if not div:
        return None
    
    div_str = div.lower().strip()
    
    if "division iii" in div_str:
        return "ncaa_d3"
    elif "division ii" in div_str:
        return "ncaa_d2"
    elif "division i" in div_str:
        return "ncaa_d1"
    elif "naia" in div_str:
        return "naia"
    elif "njcaa iii" in div_str:
        return "njcaa_iii"
    elif "njcaa ii" in div_str:
        return "njcaa_ii"
    elif "njcaa i" in div_str:
        return "njcaa_i"
    
    return None

def resolve_college_id(cursor, clippd_school_name):
    # fuzzy match clippd school name to the DOE college board name
    
    # use manual map
    lookup = MANUAL_PROGRAM_NAME_MAP.get(clippd_school_name, clippd_school_name)
    
    # use our direct unitid overrides
    if isinstance(lookup, int):
        # print(f"Direct ID override. '{clippd_school_name}' to UNITID {lookup}")
        return lookup
    
    # try case-insensitive match
    cursor.execute("SELECT unit_id FROM colleges WHERE name ILIKE %s;", [lookup])
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # try trigram similarity match
    try:
        query = """
            SELECT unit_id, name, similarity(name, %s) AS score
            FROM colleges
            WHERE name %% %s OR name ILIKE %s
            ORDER BY score DESC
            LIMIT 1;
        """
        cursor.execute(query, [lookup, lookup, f"%{lookup}%"])
        result = cursor.fetchone()
        
        if result and result[2] > 0.5:
            # print(f"Fuzzy matched '{clippd_school_name}' to '{result[1]}' (Score: {result[2]:.2f})")
            return result[0]
            
    except Exception as e:
        print(f"Fuzzy match error: {e}")
        pass
    
    print(f"Could not resolve DOE college ID for '{clippd_school_name}'")
    
    return None

def resolve_program_id(cursor, clippd_school_id):
    # get our internal database id for the given clippd_id
    cursor.execute("SELECT id FROM programs WHERE clippd_id = %s;", [clippd_school_id])
    result = cursor.fetchone()
    return result[0] if result else None

def fetch_rankings_page(type_param, gender, division, limit, offset):
    # helper function to fetch the rankings api
    params = {
        "rankingType": type_param,
        "gender": gender,
        "division": division,
        "sortField": "rank",
        "season": "2026",
        "limit": limit,
        "offset": offset
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(CLIPPD_RANKINGS_API_BASE_URL, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API returned status code: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"Request error: {e}")
        return None


# Core pipeline functions
def ingest_all_rankings(type_param):
    # get the rankings across all divisions and genders
    if not type_param in ("Team", "Player"):
        print(f"Please provide a valid of type of 'Team' or 'Player'!")
        return None
    
    LIMIT = 500
    
    genders = ["Men", "Women"]
    divisions = [
        "NCAA Division I",
        "NCAA Division II",
        "NCAA Division III",
        "NAIA",
        "NJCAA I",
        "NJCAA II",
        "NJCAA III",
    ]
    
    all_rankings = []
    
    print("Beginning Clippd API ingestion for programs...")
    
    for gen in genders:
        for div in divisions:
            has_more = True
            offset = 0
            
            while has_more:
                print(f"Fetching offset {offset}")
                data = fetch_rankings_page(type_param, gen, div, LIMIT, offset)
                
                if not data:
                    print("[!] Failed to fetch data. Aborting loop to protect database integrity.")
                    break
                
                results = data.get("results", [])
                
                if not results:
                    print("No more records found. Reached end of dataset.")
                    has_more = False
                    break
                
                all_rankings.extend(results)
                
                offset += LIMIT
                
                time.sleep(1)
                
    print(f"Total {type_param}s retrieved: {len(all_rankings)}")
    
    return all_rankings
        
# Check local json cache before calling ingesting all programs
def get_rankings_data(type_param):
    if not type_param in ("Team", "Player"):
        print(f"Please provide a valid of type of 'Team' or 'Player'!")
        return None
        
    cache_file = PROGRAM_CACHE_FILE_PATH if type_param == "Team" else PLAYER_CACHE_FILE_PATH
    
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        
        if file_age < CACHE_EXPIRATION_SECONDS:
            print(f"{type_param} json cache is still valid. Age: {file_age}. Bypassing server requests...")
            with open(cache_file, "r") as f:
                return json.load(f)
            
        else:
            print("Cache has expired. Fetching updated program rankings...")
            
    else:
        print("Could not find local cache. Fetching updated program rankings...")
        
    fresh_data = ingest_all_rankings(type_param)
    
    with open(cache_file, "w") as f:
        json.dump(fresh_data, f, indent=2)
        
    print("Saved program rankings to local cache")
    
    return fresh_data

def seed_program_rankings():
    conn = psycopg2.connect(
        host=DB_BIND_ADDRESS,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # enable pg_trm extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    conn.commit()
    
    print("Calling program rankings api for data...")
    api_payload = get_rankings_data("Team")
    
    print("Starting program ranking ingestion and entity resolution...")
    for item in api_payload:
        school_name = item.get("schoolName")
        
        college_id = resolve_college_id(cursor, school_name)
        if not college_id:
            # do not seed if we can't find the college id. protects database safety.
            continue
        
        gender = item.get("gender", "Men").lower()
        division = map_division(item.get("division"))
        clippd_id = item.get("schoolId")
        
        total_rounds = int(item.get("strokePlayRounds", 0)) + int(item.get("matchPlayRounds", 0))
        
        program_record = {
            "college_id": college_id,
            "clippd_id": clippd_id,
            "gender": gender,
            "name": school_name,
            "conference": item.get("conference"),
            "division": division,
            "head_coach": None, # scraped later on
            "rank": item.get("rank"),
            "scoring_avg": item.get("averageScore"),
            "adjusted_scoring_avg": item.get("adjustedScore"),
            "top3_finishes": item.get("eventsTop3"),
            "total_rounds": total_rounds,
            "win_loss_tie": item.get("winLossTie"),
            "wins": item.get("eventsWon")
        }
        
        upsert_query = """
            INSERT INTO programs (
                college_id, clippd_id, gender, name, conference, division, head_coach, 
                rank, scoring_avg, adjusted_scoring_avg, top3_finishes, total_rounds, win_loss_tie, wins
            ) VALUES (
                %(college_id)s, %(clippd_id)s, %(gender)s, %(name)s, %(conference)s, %(division)s, %(head_coach)s,
                %(rank)s, %(scoring_avg)s, %(adjusted_scoring_avg)s, %(top3_finishes)s, %(total_rounds)s, %(win_loss_tie)s, %(wins)s
            )
            ON CONFLICT (clippd_id) DO UPDATE SET
                college_id = EXCLUDED.college_id,
                name = EXCLUDED.name,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                rank = EXCLUDED.rank,
                scoring_avg = EXCLUDED.scoring_avg,
                adjusted_scoring_avg = EXCLUDED.adjusted_scoring_avg,
                top3_finishes = EXCLUDED.top3_finishes,
                total_rounds = EXCLUDED.total_rounds,
                win_loss_tie = EXCLUDED.win_loss_tie,
                wins = EXCLUDED.wins
        """
        
        cursor.execute(upsert_query, program_record)
        conn.commit()
        
    print("Ingestion complete! Team records resolved and upserted successfully!")
    
    cursor.close()
    conn.close()

def seed_player_rankings():
    conn = psycopg2.connect(
        host=DB_BIND_ADDRESS,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    print("Calling player rankings api for data...")
    api_payload = get_rankings_data("Player")
    
    print("Starting player ranking ingestion and entity resolution...")
    
    for item in api_payload:
        name = item.get("playerName")

        program_clippd_id = item.get("schoolId")
        player_id = item.get("playerId")
        
        program_uuid = resolve_program_id(cursor, program_clippd_id)
        program_name = item.get("schoolName")
        if not program_uuid:
            print(f"Could not resolve program uuid for player id: {player_id} player name: {name} program clippd id: {program_clippd_id} program name: {program_name}")
            continue
            
        total_rounds = int(item.get("strokePlayRounds", 0)) + int(item.get("matchPlayRounds", 0))
            
        player_record = {
            "program_uuid": program_uuid,
            "clippd_id": player_id,
            "name": name,
            "rank": item.get("rank"),
            "scoring_avg": item.get("averageScore"),
            "adjusted_scoring_avg": item.get("adjustedScore"),
            "top3_finishes": item.get("eventsTop3"),
            "total_rounds": total_rounds,
            "win_loss_tie": item.get("winLossTie"),
            "wins": item.get("eventsWon"),
            "graduation_year": None # not included in api
        }
            
        upsert_query = """
            INSERT INTO players (
                program_uuid, clippd_id, name, rank, scoring_avg, adjusted_scoring_avg, top3_finishes, total_rounds, win_loss_tie, wins, graduation_year
            ) VALUES (
                %(program_uuid)s, %(clippd_id)s, %(name)s, %(rank)s, %(scoring_avg)s, %(adjusted_scoring_avg)s,
                %(top3_finishes)s, %(total_rounds)s, %(win_loss_tie)s, %(wins)s, %(graduation_year)s
            )
            ON CONFLICT (clippd_id) DO UPDATE SET
                program_uuid = EXCLUDED.program_uuid,
                name = EXCLUDED.name,
                rank = EXCLUDED.rank,
                scoring_avg = EXCLUDED.scoring_avg,
                adjusted_scoring_avg = EXCLUDED.adjusted_scoring_avg,
                top3_finishes = EXCLUDED.top3_finishes,
                total_rounds = EXCLUDED.total_rounds,
                win_loss_tie = EXCLUDED.win_loss_tie,
                wins = EXCLUDED.wins
        """
            
        cursor.execute(upsert_query, player_record)
        conn.commit()
            
    print("Ingestion complete! Player records resolved and upserted successfully!")
        
    cursor.close()
    conn.close()
    
        
if __name__ == "__main__":
    seed_program_rankings()
    seed_player_rankings()