import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in placement.db:')
for t in tables:
    print(f'  - {t[0]}')

conn.close()
