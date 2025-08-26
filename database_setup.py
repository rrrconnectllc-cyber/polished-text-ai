# database_setup.py (Corrected Version)
import sqlite3
from datetime import date

DB_FILE = "polished_text.db"

def initialize_database():
    """Creates the database and tables with all required columns."""
    db_connection = sqlite3.connect(DB_FILE)
    cursor = db_connection.cursor()

    # Create the 'users' table with all the new columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        usage_count INTEGER NOT NULL DEFAULT 0,
        last_quota_reset TEXT NOT NULL
    )
    """)

    # Create the 'documents' table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        original_text TEXT NOT NULL,
        polished_text TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    print("✅ Database initialized successfully with all columns.")

    db_connection.commit()
    db_connection.close()

if __name__ == "__main__":
    initialize_database()
