# upgrade_db_v4.py
import sqlite3
DB_FILE = "polished_text.db"
db = sqlite3.connect(DB_FILE)
cursor = db.cursor()
try:
    # Recreate the table with the new NOT NULL constraint
    # This is the safest way in SQLite to add a NOT NULL constraint
    cursor.execute('BEGIN TRANSACTION;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            usage_count INTEGER NOT NULL DEFAULT 0,
            last_quota_reset TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT
        )
    ''')
    cursor.execute('INSERT INTO users_new SELECT id, username, password_hash, created_at, usage_count, last_quota_reset, email, phone_number FROM users')
    cursor.execute('DROP TABLE users')
    cursor.execute('ALTER TABLE users_new RENAME TO users')
    cursor.execute('COMMIT;')
    print("✅ 'email' column is now required and unique.")
except Exception as e:
    cursor.execute('ROLLBACK;')
    print(f"An error occurred: {e}")
finally:
    db.close()
