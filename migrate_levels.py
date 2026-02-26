"""
Database migration for company level progress system
"""
import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create company_level_progress table
cursor.execute("""
CREATE TABLE IF NOT EXISTS company_level_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    company_name TEXT,
    level INTEGER,
    best_score INTEGER DEFAULT 0,
    unlocked INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()
print("Company level progress table created!")
