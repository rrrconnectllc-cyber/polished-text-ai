# upgrade_db_v3.py
import sqlite3

DB_FILE = "polished_text.db"

def upgrade_database():
    """Adds optional email and phone_number columns to the 'users' table."""
    db_connection = sqlite3.connect(DB_FILE)
    cursor = db_connection.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("✅ Added 'email' column.")
    except sqlite3.OperationalError:
        print("👍 'email' column already exists.")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
        print("✅ Added 'phone_number' column.")
    except sqlite3.OperationalError:
        print("👍 'phone_number' column already exists.")
            
    db_connection.commit()
    db_connection.close()
    print("\nDatabase upgrade complete.")

if __name__ == "__main__":
    upgrade_database()
