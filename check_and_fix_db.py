import sqlite3
from datetime import date

conn = sqlite3.connect('placement.db')
cursor = conn.cursor()

# Check if xp_points exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='xp_points'")
if not cursor.fetchone():
    print("Creating xp_points table...")
    cursor.execute('''
    CREATE TABLE xp_points (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        xp INTEGER DEFAULT 0,
        level TEXT DEFAULT 'Beginner',
        daily_streak INTEGER DEFAULT 0,
        last_active_date DATE,
        total_quizzes INTEGER DEFAULT 0,
        total_accuracy REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
# Initialize XP records for existing users
cursor.execute('SELECT id FROM users')
users = cursor.fetchall()
today = date.today()

print(f"Found {len(users)} users")

for user in users:
    user_id = user[0]
    try:
        cursor.execute('INSERT INTO xp_points (user_id, xp, level, daily_streak, last_active_date) VALUES (?, 0, "Beginner", 0, ?)', (user_id, today))
        print(f"Added XP record for user {user_id}")
    except:
        pass  # Already exists

conn.commit()

# Verify
cursor.execute('SELECT COUNT(*) FROM xp_points')
xp_count = cursor.fetchone()[0]
print(f"XP records: {xp_count}")

conn.close()
print("Done!")
