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
def parse_head_coach(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    coach_label = soup.find(string=re.compile(r"Head Coach", re.IGNORECASE))
    
    if coach_label:
        coach_name = coach_label.find_next()
        if coach_name:
            return coach_name.text.strip()
        
    return None

# playwright configuration
def configure_page_route(page):
    # abort background network traffic
    page.route("**/*sentry*", lambda route: route.abort())
    page.route("**/*google-analytics*", lambda route: route.abort())
    page.route("**/*hotjar*", lambda route: route.abort())
    page.route("**/*doubleclick*", lambda route: route.abort())

def scrape_program_details():
    conn = psycopg2.connect(
        host=DB_BIND_ADDRESS,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, clippd_id, name FROM programs WHERE clippd_id LIKE '%2883%';")
    programs = cursor.fetchall()
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)
        
        configure_page_route(page) # apply telemetry blockers
        
        for program_id, clippd_id, name in programs:
        
            program_url = f"https://scoreboard.clippd.com/teams/{clippd_id}?season=2026"
            
            try:
                page.goto(program_url, wait_until="load", timeout=15000)
                page.wait_for_selector("main", timeout=5000) # wait for the main content to load before parsing
                
                html_content = page.content()
                #with open(HTML_FILE, "w", encoding="utf-8") as file:
                    #file.write(html_content)
                
                coach = parse_head_coach(html_content)
                print(coach)
                
            except Exception as e:
                print(f"Error fetching id {clippd_id}: {e}")
                conn.rollback()   
                
        browser.close()

if __name__ == "__main__":
    scrape_program_details()