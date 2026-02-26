import sqlite3
DB_PATH = 'placement.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%company%'")
tables = [r[0] for r in cursor.fetchall()]
print('Company tables:', tables)
conn.close()
