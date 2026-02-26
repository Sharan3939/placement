import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check coding problems
cursor.execute('SELECT id, title, difficulty FROM coding_problems')
problems = cursor.fetchall()
print('Coding Problems:', problems)
print('Count:', len(problems))

# Check difficulty distribution
cursor.execute('SELECT difficulty, COUNT(*) FROM coding_problems GROUP BY difficulty')
diff_dist = cursor.fetchall()
print('Difficulty distribution:', diff_dist)

# Check if there's a section mapping for company mocks
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

conn.close()
