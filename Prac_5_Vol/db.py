# db.py

import sqlite3
from utils import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS news (
        guid TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        published_at TEXT,
        comments_count INTEGER,
        rating INTEGER,
        created_at_utc TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
