"""
Database Migration Script v2
Adds missing tables for Phase 1-3 features
"""

import sqlite3
from datetime import date

DB_PATH = 'placement.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add new tables if they don't exist

# 1. user_stats table
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

# 2. category_performance table
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

# 3. xp_history table
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

# 4. streak_tracking table
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

# 5. badges master table - Stores badge definitions
cursor.execute('''
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    xp_required INTEGER DEFAULT 0,
    description TEXT,
    icon TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 6. user_badges table - Links users to earned badges
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id),
    UNIQUE(user_id, badge_id)
)
''')

# Insert default badges if they don't exist
default_badges = [
    (1, 'Bronze', 100, 'Earn 100 XP to unlock this badge', '🥉'),
    (2, 'Silver', 500, 'Earn 500 XP to unlock this badge', '🥈'),
    (3, 'Gold', 1000, 'Earn 1000 XP to unlock this badge', '🥇'),
    (4, 'Platinum', 2000, 'Earn 2000 XP to unlock this badge', '💎'),
]

for badge_id, name, xp_required, description, icon in default_badges:
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO badges (id, name, xp_required, description, icon)
            VALUES (?, ?, ?, ?, ?)
        ''', (badge_id, name, xp_required, description, icon))
    except:
        pass

# Initialize records for existing users
cursor.execute('SELECT id FROM users')
users = cursor.fetchall()
today = date.today()

print("Initializing user data...")

for user in users:
    user_id = user[0]
    try:
        cursor.execute('INSERT INTO xp_points (user_id, xp, level, daily_streak, last_active_date) VALUES (?, 0, "Beginner", 0, ?)', (user_id, today))
        print(f"Added xp_points for user {user_id}")
    except:
        pass
    
    try:
        cursor.execute('INSERT INTO streak_tracking (user_id, current_streak, longest_streak, last_login_date, total_login_days) VALUES (?, 0, 0, ?, 0)', (user_id, today))
        print(f"Added streak_tracking for user {user_id}")
    except:
        pass
    
    try:
        cursor.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
        print(f"Added user_stats for user {user_id}")
    except:
        pass

conn.commit()
print('\n✅ Database migration completed successfully!')
print('\nTables created/verified:')
print('- user_stats')
print('- category_performance')
print('- xp_history')
print('- streak_tracking')
print('- badges')
print('- user_badges')

conn.close()
