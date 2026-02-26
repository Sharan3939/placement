"""
Phase 2: Adaptive Difficulty System
Functions for tracking user performance and recommending difficulty levels.
"""

from flask import session, jsonify
from datetime import date


def calculate_recommended_difficulty(accuracy, current_difficulty):
    """
    Calculate recommended difficulty based on user performance.
    - If accuracy > 80% → Increase difficulty
    - If accuracy < 50% → Suggest easier
    - Otherwise → Keep same difficulty
    """
    difficulty_order = ['Easy', 'Medium', 'Hard']
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


def update_category_performance(user_id, quiz_id, difficulty, score, total, get_db_connection):
    """Update user's performance in a category."""
    from datetime import date
    
    percentage = (score / total * 100) if total > 0 else 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM category_performance WHERE user_id = ? AND quiz_id = ?", (user_id, quiz_id))
    existing = cursor.fetchone()
    
    if existing:
        new_attempts = existing['attempts'] + 1
        new_correct = existing['correct_answers'] + score
        new_total = existing['total_questions'] + total
        new_accuracy = (new_correct / new_total * 100) if new_total > 0 else 0
        recommended, change_type = calculate_recommended_difficulty(new_accuracy, difficulty)
        
        cursor.execute("""UPDATE category_performance SET attempts = ?, correct_answers = ?, 
            total_questions = ?, average_accuracy = ?, last_attempt = ?, recommended_difficulty = ?
            WHERE user_id = ? AND quiz_id = ?""", 
            (new_attempts, new_correct, new_total, new_accuracy, date.today(), recommended, user_id, quiz_id))
    else:
        recommended, change_type = calculate_recommended_difficulty(percentage, difficulty)
        cursor.execute("""INSERT INTO category_performance 
            (user_id, quiz_id, attempts, correct_answers, total_questions, average_accuracy, last_attempt, recommended_difficulty)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?)""", (user_id, quiz_id, score, total, percentage, date.today(), recommended))
    
    conn.commit()
    conn.close()
    
    return {'accuracy': percentage, 'recommended_difficulty': recommended, 'change_type': change_type}


def get_difficulty_message(accuracy, recommended):
    """Get a user-friendly message about difficulty recommendation."""
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
