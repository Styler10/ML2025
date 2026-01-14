import requests
import sqlite3
import uuid
import logging
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

import re
from datetime import datetime


DB_NAME = "news.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

MONTHS_RU = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

def parse_banki_date(text: str) -> str | None:
    """
    '10 декабря 2025 г.' -> ISO
    """
    if not text:
        return None

    m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", text.lower())
    if not m:
        return None

    day = int(m.group(1))
    month = MONTHS_RU.get(m.group(2))
    year = int(m.group(3))

    if not month:
        return None

    dt = datetime(year, month, day)
    return dt.isoformat()



def fetch(url: str) -> BeautifulSoup:
    logging.info(f"FETCH {url}")

    r = requests.get(url, headers=HEADERS, timeout=15)

    # КРИТИЧНО: принудительная корректировка кодировки
    if r.encoding is None or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding

    return BeautifulSoup(r.text, "lxml")


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\S\r\n]+", " ", text)

    return text.strip()


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def gen_uuid():
    return str(uuid.uuid4())


def save_to_db(item: dict):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO news VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item["guid"],
        item["title"],
        item["description"],
        item["url"],
        item["published_at"],
        item["comments_count"],
        item["rating"],
        item["created_at_utc"]
    ))

    conn.commit()
    conn.close()
