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
        
    
    