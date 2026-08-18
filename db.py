"""
Stage 2: STORAGE
------------------
SQLite is used here instead of Postgres/MySQL on purpose: it's a single
file, needs zero setup, and is plenty for a few thousand job postings.
This is the same reasoning you'd apply picking infra for a small internal
tool at work — don't over-provision for the scale you don't have yet.
"""
import sqlite3

DB_PATH = "jobs.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            company TEXT,
            description TEXT,
            url TEXT,
            location TEXT,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, company, source)
        )
    """)
    conn.commit()
    conn.close()


def insert_job(job):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO jobs (source, title, company, description, url, location)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (job["source"], job["title"], job["company"], job["description"],
             job["url"], job["location"]),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_jobs(role_filter=None, company_filter=None):
    conn = get_conn()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if role_filter:
        query += " AND title LIKE ?"
        params.append(f"%{role_filter}%")
    if company_filter:
        query += " AND company LIKE ?"
        params.append(f"%{company_filter}%")
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_distinct_companies():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT company FROM jobs ORDER BY company").fetchall()
    conn.close()
    return [r["company"] for r in rows]
