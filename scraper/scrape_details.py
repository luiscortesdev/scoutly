import os
import re
import json
import time
from datetime import datetime, date
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

CACHE_DIR = os.path.join("scraper", ".cache")
PROGRAM_DETAILS_CACHE_PATH = os.path.join(CACHE_DIR, "clippd_program_details.json")
PLAYER_DETAILS_CACHE_PATH = os.path.join(CACHE_DIR, "clippd_player_details.json")

os.makedirs(CACHE_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# helper cache functions
def load_json_cache(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return json.load(f)

    return {}

def save_json_cache(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# parsing functions
def parse_date_str(date_str):
    if not date_str or not "," in date_str:
        return None, None
    
    def parse_mm_dd(mm_dd_str):
        mm_str = mm_dd_str.split(" ")[0]
        dd_str = mm_dd_str.split(" ")[1]
        
        mm = None
        match mm_str:
            case "jan": mm = 1
            case "feb": mm = 2
            case "mar": mm = 3
            case "apr": mm = 4
            case "may": mm = 5
            case "jun": mm = 6
            case "jul": mm = 7
            case "aug": mm = 8
            case "sep": mm = 9
            case "oct": mm = 10
            case "nov": mm = 11
            case "dec": mm = 12
                
        dd = None
        if dd_str:
            try:
                dd = int(dd_str)
            except ValueError:
                pass
            
        return mm, dd
    
    comma_split = date_str.split(",")
    
    day_month_str = comma_split[0].lower().strip()

    # ensure a hyphen exists in the day month string before splitting
    # events without a hyphen are one day
    if "-" in day_month_str:
        start_date_str = day_month_str.split("-")[0].lower().strip()
        end_date_str = day_month_str.split("-")[1].lower().strip()
    else:
        start_date_str = day_month_str
        end_date_str = day_month_str
    
    start_date_mm, start_date_dd = parse_mm_dd(start_date_str)
    end_date_mm, end_date_dd = parse_mm_dd(end_date_str)
    
    year_str = comma_split[1].strip()
    year = None
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            pass

    try:
        start_date = date(year, start_date_mm, start_date_dd)
        end_date = date(year, end_date_mm, end_date_dd)
        
        return start_date, end_date
    except Exception:
        print(f"Error parsing start and end date for event")
        return None, None

def parse_head_coach(soup):
    coach_label = soup.find(string=re.compile(r"Head Coach", re.IGNORECASE))
    
    if coach_label:
        coach_name = coach_label.find_next()
        if coach_name:
            return coach_name.text.strip()
        
    return None

def parse_graduation_year(soup):
    school_year_label = soup.find(string=re.compile(r"School Year", re.IGNORECASE))

    if school_year_label:
        graduation_year_label = school_year_label.find_next()
        if graduation_year_label:
            return graduation_year_label.text.strip()

def parse_events(soup, uuid):
    events = []
    
    rows = soup.find_all("tr")
    
    for row in rows:
        cells = row.find_all("td")
        
        if len(cells) < 6:
            continue
        
        try:
            info_cell = cells[0]
            span_tags = info_cell.find_all("span")
            
            name_span = span_tags[0]
            name = name_span.text.strip() if name_span else None
            if not name:
                img_tag = info_cell.find("img")
                name = img_tag.get("alt", "").strip() if img_tag else "Unknown Tournament"
                
            date_span = span_tags[1]
            date_str = date_span.text.strip() if date_span else None
            
            start_date, end_date = parse_date_str(date_str)
            
            position_cell = cells[1]
            position = position_cell.text
            field_size = None
            
            # some event rows contain the field size and position within a p tag
            position_cell_p_tag = position_cell.find("p")
            if position_cell_p_tag:
                position_cell_strings = list(position_cell_p_tag.stripped_strings)
                
                position = position_cell_strings[0]
                field_size = position_cell_strings[2]
                
            score_cell = cells[2]
            score = score_cell.text
            
            event_sg_cell = cells[3]
            event_sg_text = event_sg_cell.text.strip()
            event_sg_cleaned = re.sub(r"[^\d\.-]", "", event_sg_text)
            event_sg = float(event_sg_cleaned) if event_sg_cleaned else 0.0
            
            total_points_cell = cells[4]
            total_points_cell_p_tag = total_points_cell.find("p")
            if total_points_cell_p_tag:
                total_points_cell_strings = list(total_points_cell_p_tag.stripped_strings)

                total_points_cleaned = re.sub(r"[^\d\.-]", "", total_points_cell_strings[0])
                total_points = round(float(total_points_cleaned), 3) if total_points_cleaned else 0.0

                # ensure that the rounds string exists
                if len(total_points_cell_strings) > 1:
                    total_rounds_cleaned = re.sub(r"[^\d]", "", total_points_cell_strings[1])
                    total_rounds = int(total_rounds_cleaned) if total_rounds_cleaned else 0

            weighted_points_cell = cells[5]
            weighted_points_text = weighted_points_cell.text.strip()
            weighted_points_cleaned = re.sub(r"[^\d\.-]", "", weighted_points_text)
            weighted_points = float(weighted_points_cleaned) if weighted_points_cleaned else 0.0

            event_tuple = (
                uuid,
                name,
                position,
                field_size,
                score,
                event_sg,
                total_points,
                weighted_points,
                total_rounds,
                start_date,
                end_date
            )

            events.append(event_tuple)
        
        except Exception as e:
            print(f"Error parsing event row: {e}")

    return events
            

# playwright configuration
def configure_page_route(page):
    def handle_route(route, request):
        url = request.url
        resource_type = request.resource_type
        
        blocked_trackers = ["sentry", "google.analytics", "hotjar", "doubleclick", "quantserve", "intergient", "rapidedge", "quantcount"]
        blocked_assets = ["image", "font", "media"]
        
        # match to our block lists
        if any(tracker in url.lower() for tracker in blocked_trackers):
            route.abort()
        elif resource_type in blocked_assets:
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle_route)

def scrape_program_details():
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=DB_BIND_ADDRESS,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, clippd_id, name FROM programs WHERE clippd_id LIKE '%%3070%%';")
    programs = cursor.fetchall()
    
    print(f"Found {len(programs)} programs to process.")
    if not programs:
        cursor.close()
        conn.close()
        return

    cache_file = load_json_cache(PROGRAM_DETAILS_CACHE_PATH)

    # Using sync_playwright as a standard flat context manager
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # Create a single context and page OUTSIDE the loop to prevent process leaks
        page = browser.new_page(user_agent=USER_AGENT)
        configure_page_route(page)
        
        for program_id, clippd_id, name in programs:
            program_url = f"https://scoreboard.clippd.com/teams/{clippd_id}?season=2026"
            
            try:
                if clippd_id in cache_file:
                    print(f"Loaded {name} ({clippd_id}) data from JSON cache. Bypassing Playwright...")
                    cached_data = cache_file[clippd_id]
                    coach = cached_data["head_coach"]
                    
                    # Convert dates from JSON string back to datetime.date objects for insertion
                    events = []
                    for e in cached_data["events"]:
                        s_dt = datetime.strptime(e["start_date"], "%Y-%m-%d").date() if e["start_date"] else None
                        e_dt = datetime.strptime(e["end_date"], "%Y-%m-%d").date() if e["end_date"] else None
                        events.append((
                            program_id, e["name"], e["position"], e["field_size"], e["score"],
                            e["event_sg"], e["total_points"], e["weighted_points"], e["total_rounds"],
                            s_dt, e_dt
                        ))
                else:
                    print(f"Getting fresh program data for {name} ({clippd_id})")
                    page.goto(program_url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_selector("main", timeout=5000)
                    
                    html_content = page.content()
                    soup = BeautifulSoup(html_content, "html.parser")
                    
                    coach = parse_head_coach(soup)

                    events_tuples = parse_events(soup, program_id)

                    cache_file[clippd_id] = {
                        "head_coach": coach,
                        "events": [
                            {
                                "name": e[1], "position": e[2], "field_size": e[3], "score": e[4],
                                "event_sg": e[5], "total_points": e[6], "weighted_points": e[7], "total_rounds": e[8],
                                "start_date": e[9].strftime("%Y-%m-%d") if e[9] else None,
                                "end_date": e[10].strftime("%Y-%m-%d") if e[10] else None
                            } for e in events_tuples
                        ]
                    }

                    save_json_cache(PROGRAM_DETAILS_CACHE_PATH, cache_file)

                    events = events_tuples

                # insert coach into database
                if coach:
                    try:
                        cursor.execute("UPDATE programs SET head_coach = %s WHERE id = %s;", [coach, program_id])
                        print(f"Updated {name} head coach to {coach}")
                    except Exception as e:
                        print(f"Error updating head coach {e}")

                # we delete and reload events to ensure up to date events for the programs
                if events:
                    try:
                        cursor.execute("DELETE FROM program_events WHERE program_uuid = %s;", [program_id])

                        events_insert_query = """
                            INSERT INTO program_events (
                                program_uuid, name, position, field_size, score, 
                                event_sg, total_points, weighted_points, total_rounds, 
                                start_date, end_date
                            ) VALUES %s;
                        """

                        execute_values(cursor, events_insert_query, events)
                        print(f"Reloaded {len(events)} events for {name}.")
                    except Exception as e:
                        print(f"Error updating events for {name} ({clippd_id})")

                conn.commit()

            except Exception as e:
                (f"Error fetching id {clippd_id}: {e}")
                conn.rollback()
        
        page.close()
        browser.close()

    cursor.close()
    conn.close()

def scrape_player_details():
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=DB_BIND_ADDRESS,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, clippd_id, name FROM players WHERE clippd_id LIKE '%%19552%%';")
    players = cursor.fetchall()
    
    print(f"Found {len(players)} players to process.")
    if not players:
        cursor.close()
        conn.close()
        return

    # Using sync_playwright as a standard flat context manager
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # Create a single context and page OUTSIDE the loop to prevent process leaks
        page = browser.new_page(user_agent=USER_AGENT)
        configure_page_route(page)
        
        for player_id, clippd_id, name in players:
            player_url = f"https://scoreboard.clippd.com/players/{clippd_id}?season=2026"
            
            try:
                page.goto(player_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_selector("main", timeout=5000)
                
                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                events = parse_events(soup, player_id)

                graduation_year = parse_graduation_year(soup)
                if graduation_year:
                    try:
                        cursor.execute("UPDATE players SET graduation_year = %s WHERE id = %s;", [graduation_year, player_id])
                        print(f"Updated {name} grad year to {graduation_year}")
                    except Exception as e:
                        print(f"Error updating player grad year {e}")

                # we delete and reload events to ensure up to date events for the programs
                if events:
                    cursor.execute("DELETE FROM player_events WHERE player_uuid = %s;", [player_id])

                    events_insert_query = """
                        INSERT INTO player_events (
                            player_uuid, name, position, field_size, score, 
                            event_sg, total_points, weighted_points, total_rounds, 
                            start_date, end_date
                        ) VALUES %s;
                    """

                    execute_values(cursor, events_insert_query, events)
                    print(f"Reloaded {len(events)} events for {name}.")

                conn.commit()

            except Exception as e:
                (f"Error fetching id {clippd_id}: {e}")
                conn.rollback()
        
        page.close()
        browser.close()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    scrape_program_details()
    #scrape_player_details()