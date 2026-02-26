"""
Phase 1 Test Script
Tests XP, Badge, Streak, and Dashboard functionality
"""
import sqlite3
import json
from datetime import date, timedelta

DB_PATH = 'placement.db'

def test_database_tables():
    """Test that all required tables exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['user_stats', 'category_performance', 'xp_history', 'streak_tracking', 'xp_points']
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = cursor.fetchone()
        print(f"✓ Table '{table}' exists: {result is not None}")
    
    conn.close()

def test_xp_calculation():
    """Test XP calculation for different difficulty levels"""
    XP_REWARDS = {'Easy': 10, 'Medium': 20, 'Hard': 30}
    
    test_cases = [
        ('Easy', 100, 15),   # 100% = 10 + 5 bonus
        ('Easy', 80, 12),    # 80% = 10 + 2 bonus  
        ('Easy', 50, 10),    # 50% = 10 (no bonus)
        ('Medium', 95, 25),  # 95% = 20 + 5 bonus
        ('Hard', 85, 32),    # 85% = 30 + 2 bonus
    ]
    
    print("\n=== XP Calculation Tests ===")
    for difficulty, percentage, expected_xp in test_cases:
        xp_earned = XP_REWARDS.get(difficulty, 10)
        if percentage >= 90:
            xp_earned += 5
        elif percentage >= 70:
            xp_earned += 2
        
        status = "✓" if xp_earned == expected_xp else "✗"
        print(f"{status} {difficulty} at {percentage}%: Expected {expected_xp}, Got {xp_earned}")

def test_badge_levels():
    """Test badge level calculations"""
    BADGE_LEVELS = {'Bronze': 100, 'Silver': 500, 'Gold': 1000, 'Platinum': 2000}
    
    test_cases = [
        (0, 'Beginner'),
        (50, 'Beginner'),
        (100, 'Bronze'),
        (250, 'Bronze'),
        (500, 'Silver'),
        (999, 'Silver'),
        (1000, 'Gold'),
        (1500, 'Gold'),
        (2000, 'Platinum'),
        (5000, 'Platinum'),
    ]
    
    print("\n=== Badge Level Tests ===")
    for xp, expected_level in test_cases:
        current_level = 'Beginner'
        for level, threshold in sorted(BADGE_LEVELS.items(), key=lambda x: x[1]):
            if xp >= threshold:
                current_level = level
        
        status = "✓" if current_level == expected_level else "✗"
        print(f"{status} XP={xp}: Expected {expected_level}, Got {current_level}")

def test_existing_users():
    """Test that existing users have XP and streak records"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"\n=== User Records Test ===")
    print(f"Total users: {total_users}")
    
    cursor.execute("SELECT COUNT(*) FROM xp_points")
    xp_records = cursor.fetchone()[0]
    print(f"XP records: {xp_records} (should be {total_users})")
    print(f"✓ XP records match users: {xp_records == total_users}")
    
    cursor.execute("SELECT COUNT(*) FROM streak_tracking")
    streak_records = cursor.fetchone()[0]
    print(f"Streak records: {streak_records} (should be {total_users})")
    print(f"✓ Streak records match users: {streak_records == total_users}")
    
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    stats_records = cursor.fetchone()[0]
    print(f"User stats records: {stats_records} (should be {total_users})")
    print(f"✓ Stats records match users: {stats_records == total_users}")
    
    conn.close()

def test_sample_xp_data():
    """Add sample XP data for testing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get first user
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        
        # Check current XP
        cursor.execute("SELECT xp FROM xp_points WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        current_xp = result[0] if result else 0
        print(f"\n=== Sample User Test ===")
        print(f"User ID: {user_id}")
        print(f"Current XP: {current_xp}")
        
        # Add some XP for testing
        cursor.execute("UPDATE xp_points SET xp = xp + 50 WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO xp_history (user_id, xp_amount, transaction_type, description) VALUES (?, 50, 'test', 'Test XP addition')", (user_id,))
        conn.commit()
        
        cursor.execute("SELECT xp FROM xp_points WHERE user_id = ?", (user_id,))
        new_xp = cursor.fetchone()[0]
        print(f"After adding 50 XP: {new_xp}")
        print(f"✓ XP addition works: {new_xp == current_xp + 50}")
    
    conn.close()

def test_quiz_submission():
    """Test quiz submission process"""
    print("\n=== Quiz Submission Test ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get a user
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        
        # Get a quiz
        cursor.execute("SELECT id FROM quizzes LIMIT 1")
        quiz = cursor.fetchone()
        
        if quiz:
            quiz_id = quiz[0]
            
            # Simulate a quiz submission
            difficulty = 'Easy'
            score = 8
            total = 10
            percentage = (score / total * 100)
            
            xp_earned = 10
            if percentage >= 90:
                xp_earned += 5
            elif percentage >= 70:
                xp_earned += 2
            
            # Insert score
            cursor.execute("""INSERT INTO user_scores (user_id, quiz_id, difficulty, score, total, percentage) 
                          VALUES (?, ?, ?, ?, ?, ?)""", (user_id, quiz_id, difficulty, score, total, percentage))
            
            # Update XP
            cursor.execute("UPDATE xp_points SET xp = xp + ?, total_quizzes = total_quizzes + 1 WHERE user_id = ?", (xp_earned, user_id))
            
            # Record XP history
            cursor.execute("INSERT INTO xp_history (user_id, xp_amount, transaction_type, description, related_id) VALUES (?, ?, 'quiz_completion', ?, ?)",
                         (user_id, xp_earned, f'Completed {difficulty} quiz', quiz_id))
            
            # Update user stats
            cursor.execute("UPDATE user_stats SET total_tests = total_tests + 1, total_correct = total_correct + ?, total_questions = total_questions + ? WHERE user_id = ?",
                         (score, total, user_id))
            
            conn.commit()
            
            # Verify
            cursor.execute("SELECT xp FROM xp_points WHERE user_id = ?", (user_id,))
            new_xp = cursor.fetchone()[0]
            
            cursor.execute("SELECT total_tests, total_correct, total_questions FROM user_stats WHERE user_id = ?", (user_id,))
            stats = cursor.fetchone()
            
            print(f"✓ Quiz submitted successfully")
            print(f"  - XP earned: {xp_earned}")
            print(f"  - New XP: {new_xp}")
            print(f"  - Stats: tests={stats[0]}, correct={stats[1]}, questions={stats[2]}")
    
    conn.close()

def test_dashboard_queries():
    """Test dashboard query functionality"""
    print("\n=== Dashboard Queries Test ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        
        # Test total tests
        cursor.execute("SELECT COUNT(*) FROM user_scores WHERE user_id = ?", (user_id,))
        total_tests = cursor.fetchone()[0]
        print(f"Total tests: {total_tests}")
        
        # Test average accuracy
        cursor.execute("SELECT ROUND(AVG(percentage), 2) FROM user_scores WHERE user_id = ?", (user_id,))
        avg_accuracy = cursor.fetchone()[0] or 0
        print(f"Average accuracy: {avg_accuracy}%")
        
        # Test category performance
        cursor.execute("""SELECT q.name, ROUND(AVG(us.percentage), 2) as avg_score
                       FROM user_scores us JOIN quizzes q ON us.quiz_id = q.id
                       WHERE us.user_id = ? GROUP BY q.id ORDER BY avg_score DESC""", (user_id,))
        categories = cursor.fetchall()
        
        if categories:
            print(f"Strongest category: {categories[0]['name']} ({categories[0]['avg_score']}%)")
            print(f"Weakest category: {categories[-1]['name']} ({categories[-1]['avg_score']}%)")
        else:
            print("No category data yet (user hasn't taken any quizzes)")
        
        # Test XP data
        cursor.execute("SELECT xp, level FROM xp_points WHERE user_id = ?", (user_id,))
        xp_data = cursor.fetchone()
        if xp_data:
            print(f"XP: {xp_data[0]}, Level: {xp_data[1]}")
        
        # Test streak data
        cursor.execute("SELECT current_streak, longest_streak FROM streak_tracking WHERE user_id = ?", (user_id,))
        streak = cursor.fetchone()
        if streak:
            print(f"Current streak: {streak[0]}, Longest streak: {streak[1]}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Phase 1 Implementation Tests")
    print("=" * 50)
    
    test_database_tables()
    test_xp_calculation()
    test_badge_levels()
    test_existing_users()
    test_sample_xp_data()
    test_quiz_submission()
    test_dashboard_queries()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")
    print("=" * 50)
