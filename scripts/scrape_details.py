import os
import re
import time
import requests
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DB_BIND_ADDRESS = os.getenv("DB_BIND_ADDRESS", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "scoutly")
DB_USER = os.getenv("DB_USER", "scoutly_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}