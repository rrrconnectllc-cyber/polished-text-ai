# database_setup.py
import sqlite3
from datetime import datetime

DB_FILE = "polished_text.db"

db_connection = sqlite3.connect(DB_FILE)
cursor = db_connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    polished_text TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)""")
db_connection.commit()
db_connection.close()
print("✅ Database initialized successfully.")
