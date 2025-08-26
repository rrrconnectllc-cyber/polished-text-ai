# upgrade_db_v2.py
import sqlite3
from datetime import date

DB_FILE = "polished_text.db"

def upgrade_database():
    """Adds usage tracking columns to the 'users' table."""
    db_connection = sqlite3.connect(DB_FILE)
    cursor = db_connection.cursor()

    try:
        # Add usage_count column with a default of 10 for existing users
        cursor.execute("ALTER TABLE users ADD COLUMN usage_count INTEGER NOT NULL DEFAULT 10")
        print("✅ Added 'usage_count' column.")
    except sqlite3.OperationalError:
        print("👍 'usage_count' column already exists.")

    try:
        # Add last_quota_reset column with today's date for existing users
        today_str = date.today().isoformat()
        cursor.execute("ALTER TABLE users ADD COLUMN last_quota_reset TEXT NOT NULL DEFAULT ?", (today_str,))
        print("✅ Added 'last_quota_reset' column.")
    except sqlite3.OperationalError:
        print("👍 'last_quota_reset' column already exists.")

    db_connection.commit()
    db_connection.close()
    print("\nDatabase upgrade complete.")

if __name__ == "__main__":
    upgrade_database()
