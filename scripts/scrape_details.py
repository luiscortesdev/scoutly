import os
import re
import time
import psycopg2
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# orchestration functions
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
        
        for program_id, clippd_id, name in programs:
        
            program_url = f"https://scoreboard.clippd.com/teams/{clippd_id}?season=2026"
            
            try:
                response = page.goto(program_url, wait_until="networkidle", timeout=15000)
                
                print(response.status())
                html_content = page.content()
                
            except Exception as e:
                print(f"Error fetching id {clippd_id}: {e}")
                conn.rollback()        

if __name__ == "__main__":
    scrape_program_details()