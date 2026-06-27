import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "linkednektor.db")


def init_db():
    """Initializes the database and creates the contacted_profiles table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacted_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_url TEXT UNIQUE,
            name TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def is_profile_contacted(profile_url):
    """
    Checks if a profile URL has already been contacted.
    Returns True if it has been successfully sent or is already connected.
    """
    clean_url = profile_url.rstrip("/").split("?")[0]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM contacted_profiles WHERE profile_url = ?",
        (clean_url,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        status = row[0]
        # Skip if already sent or already a connection
        return status in ("sent", "already_connected")
    return False


def add_contacted_profile(profile_url, name, status):
    """Adds or updates a profile in the contacted database."""
    clean_url = profile_url.rstrip("/").split("?")[0]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO contacted_profiles (profile_url, name, status)
            VALUES (?, ?, ?)
            ON CONFLICT(profile_url) DO UPDATE SET
                name = excluded.name,
                status = excluded.status,
                timestamp = CURRENT_TIMESTAMP
            """,
            (clean_url, name, status)
        )
        conn.commit()
    except Exception as e:
        print(f"  ⚠️ Database error: {e}")
    finally:
        conn.close()


def clear_contacted_profiles():
    """Clears all records from the contacted_profiles table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM contacted_profiles")
        conn.commit()
    except Exception as e:
        print(f"  ⚠️ Database error while clearing: {e}")
    finally:
        conn.close()
