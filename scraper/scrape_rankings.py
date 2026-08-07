import os
import time
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

CLIPPD_RANKINGS_API_BASE_URL = "https://scoreboard.clippd.com/api/rankings/leaderboard"

# helper functions
def map_division(div):
    # map clippd api divisions to our division enum
    if not div:
        return None
    
    div_str = div.lower().strip()
    
    if "division i" in div_str:
        return "ncaa_d1"
    elif "division ii" in div_str:
        return "ncaa_d2"
    elif "division iii" in div_str:
        return "ncaa_d3"
    elif "naia" in div_str:
        return "naia"
    elif "njcaa i" in div_str:
        return "njcaa_i"
    elif "njcaa ii" in div_str:
        return "njcaa_ii"
    elif "njcaa iii" in div_str:
        return "njcaa_iii"
    
    return None

def resolve_college_id(cursor, clippd_school_name):
    # fuzzy match clippd school name to the DOE college board name
    
    # try case-insensitive match
    cursor.execute("SELECT unit_id FROM colleges WHERE name ILIKE %s;", [clippd_school_name])
    
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # try trigram similarity match
    try:
        query = """
            SELECT unit_id, name, similarity(name, %s) AS score
            FROM colleges
            WHERE name % %s OR name ILIKE %s
            ORDER BY score DESC
            LIMIT 1;
        """
        cursor.execute(query, [clippd_school_name, clippd_school_name, f"%{clippd_school_name}%"])
        result = cursor.fetchone()
        
        if result and result[2] > 0.5:
            print(f"Fuzzy matched 'f{clippd_school_name}' to '{result[1]}' (Score: {result[2]:.2f})")
            
    except Exception:
        pass
    
    print(f"Could not resolve DOE college ID for '{clippd_school_name}'")
    
    return None


def ingest_program_rankings():
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
    api_payload = ingest_all_programs()
    
    print("Starting ranking ingestion and entity resolution...")
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
            ON CONFLICT (college_id, gender) DO UPDATE SET
                clippd_id = EXCLUDED.clippd_id;
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
    print("Ingestion complete! Record resolved and upserted successfully")
    
    cursor.close()
        
        
    
    