import sqlite3
from datetime import date

DB_PATH = 'placement.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add new tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    total_tests INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    average_accuracy REAL DEFAULT 0,
    strongest_category TEXT,
    weakest_category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS category_performance (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    attempts INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    average_accuracy REAL DEFAULT 0,
    last_attempt DATE,
    recommended_difficulty TEXT DEFAULT 'Easy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
    UNIQUE(user_id, quiz_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS xp_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    xp_amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    related_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS streak_tracking (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_login_date DATE,
    streak_start_date DATE,
    total_login_days INTEGER DEFAULT 0,
    bonus_xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Initialize records for existing users
cursor.execute('SELECT id FROM users')
users = cursor.fetchall()
today = date.today()

for user in users:
    user_id = user[0]
    try:
        cursor.execute('INSERT INTO xp_points (user_id, xp, level, daily_streak, last_active_date) VALUES (?, 0, "Beginner", 0, ?)', (user_id, today))
    except:
        pass
    try:
        cursor.execute('INSERT INTO streak_tracking (user_id, current_streak, longest_streak, last_login_date, total_login_days) VALUES (?, 0, 0, ?, 0)', (user_id, today))
    except:
        pass
    try:
        cursor.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
    except:
        pass

conn.commit()
print('Database updated successfully!')
conn.close()
