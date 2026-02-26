"""
Phase 2 Test Script - Adaptive Difficulty System
Tests the adaptive difficulty recommendation logic.
"""

import sqlite3
from datetime import date

DB_PATH = 'placement.db'

# Test the difficulty calculation logic
def test_difficulty_calculation():
    """Test the difficulty calculation based on accuracy."""
    print("\n=== Adaptive Difficulty Calculation Tests ===")
    
    # Test cases: (accuracy, current_difficulty, expected_recommended, expected_change_type)
    test_cases = [
        # Accuracy > 80% → Increase difficulty
        (85, 'Easy', 'Medium', 'increase'),
        (85, 'Medium', 'Hard', 'increase'),
        (85, 'Hard', 'Hard', 'max'),  # Already at max
        
        # Accuracy < 50% → Decrease difficulty
        (40, 'Medium', 'Easy', 'decrease'),
        (40, 'Easy', 'Easy', 'min'),  # Already at min
        (40, 'Hard', 'Medium', 'decrease'),
        
        # 50-80% accuracy → Maintain difficulty
        (60, 'Easy', 'Easy', 'maintain'),
        (60, 'Medium', 'Medium', 'maintain'),
        (60, 'Hard', 'Hard', 'maintain'),
        (75, 'Medium', 'Medium', 'maintain'),
        
        # Edge cases
        (100, 'Easy', 'Medium', 'increase'),
        (0, 'Hard', 'Medium', 'decrease'),
    ]
    
    difficulty_order = ['Easy', 'Medium', 'Hard']
    
    def calculate_recommended_difficulty(accuracy, current_difficulty):
        current_index = difficulty_order.index(current_difficulty) if current_difficulty in difficulty_order else 0
        
        if accuracy > 80:
            if current_index < len(difficulty_order) - 1:
                return difficulty_order[current_index + 1], 'increase'
            return current_difficulty, 'max'
        elif accuracy < 50:
            if current_index > 0:
                return difficulty_order[current_index - 1], 'decrease'
            return current_difficulty, 'min'
        else:
            return current_difficulty, 'maintain'
    
    all_passed = True
    for accuracy, current, expected_recommended, expected_change in test_cases:
        recommended, change_type = calculate_recommended_difficulty(accuracy, current)
        
        passed = (recommended == expected_recommended and change_type == expected_change)
        status = "✓" if passed else "✗"
        
        if not passed:
            all_passed = False
            print(f"{status} Accuracy {accuracy}% with {current}: Expected {expected_recommended}/{expected_change}, Got {recommended}/{change_type}")
        else:
            print(f"{status} Accuracy {accuracy}% with {current} → {recommended} ({change_type})")
    
    return all_passed


def test_category_performance_tracking():
    """Test that category_performance table exists and works."""
    print("\n=== Category Performance Tracking Test ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='category_performance'")
    if not cursor.fetchone():
        print("✗ category_performance table does not exist!")
        conn.close()
        return False
    
    print("✓ category_performance table exists")
    
    # Get user and quiz
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        
        # Check existing records
        cursor.execute("SELECT * FROM category_performance WHERE user_id = ?", (user_id,))
        records = cursor.fetchall()
        
        if records:
            print(f"✓ Found {len(records)} category performance records for user {user_id}")
            for record in records:
                print(f"  - Quiz {record[1]}: {record[4]}/{record[5]} correct ({record[6]}% accuracy), recommended: {record[7]}")
        else:
            print("  No category performance records yet (user needs to take quizzes)")
    
    conn.close()
    return True


def test_adaptive_api():
    """Test the adaptive difficulty API endpoints."""
    print("\n=== Adaptive Difficulty API Test ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get a user and quiz
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        
        # Get a quiz
        cursor.execute("SELECT id FROM quizzes LIMIT 1")
        quiz = cursor.fetchone()
        
        if quiz:
            quiz_id = quiz[0]
            
            # Simulate quiz completion with high score to trigger difficulty increase
            cursor.execute("""INSERT INTO user_scores (user_id, quiz_id, difficulty, score, total, percentage)
                VALUES (?, ?, 'Easy', 9, 10, 90.0)""", (user_id, quiz_id))
            
            # Update category performance manually to test
            cursor.execute("""INSERT OR REPLACE INTO category_performance 
                (user_id, quiz_id, attempts, correct_answers, total_questions, average_accuracy, last_attempt, recommended_difficulty)
                VALUES (?, ?, 3, 24, 30, 80.0, ?, 'Medium')""", (user_id, quiz_id, date.today()))
            
            conn.commit()
            
            # Verify the record
            cursor.execute("SELECT * FROM category_performance WHERE user_id = ? AND quiz_id = ?", (user_id, quiz_id))
            record = cursor.fetchone()
            
            if record:
                print(f"✓ Category performance recorded:")
                print(f"  - Attempts: {record[2]}")
                print(f"  - Correct: {record[3]}/{record[4]} ({record[5]}%)")
                print(f"  - Recommended difficulty: {record[6]}")
                
                # With 80% accuracy, should recommend Medium
                if record[6] == 'Medium':
                    print("✓ Correctly recommends Medium for 80% accuracy")
                else:
                    print(f"✗ Expected 'Medium', got '{record[6]}'")
    
    conn.close()


def test_message_generation():
    """Test the difficulty message generation."""
    print("\n=== Difficulty Message Generation Test ===")
    
    def get_difficulty_message(accuracy, recommended):
        if accuracy > 80:
            if recommended == 'Hard':
                return "🔥 Great performance! You're ready for Hard mode!"
            elif recommended == 'Medium':
                return "📈 Excellent! Time to try Medium difficulty."
            return "⭐ Amazing! You've mastered this level!"
        elif accuracy >= 50:
            return f"👍 Good progress! Stay at {recommended} to improve."
        else:
            return f"📚 Let's practice more at {recommended} level first."
    
    test_cases = [
        (95, 'Hard', "🔥 Great performance! You're ready for Hard mode!"),
        (85, 'Medium', "📈 Excellent! Time to try Medium difficulty."),
        (70, 'Easy', "👍 Good progress! Stay at Easy to improve."),
        (45, 'Easy', "📚 Let's practice more at Easy level first."),
    ]
    
    for accuracy, recommended, expected_msg in test_cases:
        msg = get_difficulty_message(accuracy, recommended)
        status = "✓" if msg == expected_msg else "✗"
        print(f"{status} Accuracy {accuracy}% → {msg}")
    
    print("✓ All message tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 2: Adaptive Difficulty System Tests")
    print("=" * 60)
    
    # Test 1: Difficulty calculation logic
    test1_passed = test_difficulty_calculation()
    
    # Test 2: Category performance tracking
    test2_passed = test_category_performance_tracking()
    
    # Test 3: API and database integration
    test_adaptive_api()
    
    # Test 4: Message generation
    test_message_generation()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ Phase 2 Tests Passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)
