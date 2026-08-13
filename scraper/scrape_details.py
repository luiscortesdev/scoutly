import os
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

CACHE_DIR = os.path.join("database", ".cache")
HTML_FILE = os.path.join(CACHE_DIR, "program.html")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# parsing functions
def parse_head_coach(soup):
    
    coach_label = soup.find(string=re.compile(r"Head Coach", re.IGNORECASE))
    
    if coach_label:
        coach_name = coach_label.find_next()
        if coach_name:
            return coach_name.text.strip()
        
    return None

def parse_events(soup):
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
            
            print(date_str, name)
            
            
        except Exception as e:
            print(f"Error: {e}")
            

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
    
    cursor.execute("SELECT id, clippd_id, name FROM programs WHERE clippd_id LIKE '%%2483%%';")
    programs = cursor.fetchall()
    
    print(f"Found {len(programs)} program(s) to process.")
    if not programs:
        cursor.close()
        conn.close()
        return

    # Using sync_playwright as a standard flat context manager
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # Create a single context and page OUTSIDE the loop to prevent process leaks
        page = browser.new_page(user_agent=USER_AGENT)
        configure_page_route(page)
        
        for program_id, clippd_id, name in programs:
            program_url = f"https://scoreboard.clippd.com/teams/{clippd_id}?season=2026"
            
            try:
                page.goto(program_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_selector("main", timeout=5000)
                
                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                
                coach = parse_head_coach(soup)
                if coach:
                    cursor.execute("UPDATE programs SET head_coach = %s WHERE id = %s;", [coach, program_id])
                    print(f"Updated {name} head coach to {coach}")
                    
                events = parse_events(soup)
                
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