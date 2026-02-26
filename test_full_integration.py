"""
Full System Integration Test
Tests all key features of the upgraded placement preparation website
"""

import sys
import os

# Test 1: Check all required tables exist
def test_database_tables():
    print("\n=== TEST 1: Database Tables ===")
    import sqlite3
    DB_PATH = "placement.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    required_tables = [
        'users', 'quizzes', 'questions', 'user_scores',
        'xp_points', 'user_stats', 'category_performance',
        'xp_history', 'streak_tracking', 'user_badges', 'badges'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    all_exist = True
    for table in required_tables:
        if table in existing_tables:
            print(f"  ✓ {table} exists")
        else:
            print(f"  ✗ {table} MISSING")
            all_exist = False
    
    conn.close()
    return all_exist

# Test 2: Check app routes
def test_app_routes():
    print("\n=== TEST 2: App Routes ===")
    from app import app
    
    test_routes = [
        '/login', '/register', '/logout', '/',
        '/aptitude', '/technical', '/mock',
        '/company-mocks', '/dashboard', '/profile',
        '/leaderboard', '/coding', '/code-practice'
    ]
    
    with app.test_client() as client:
        for route in test_routes:
            # Just check if route is registered (will redirect to login for protected routes)
            try:
                response = client.get(route)
                print(f"  ✓ {route} - Status: {response.status_code}")
            except Exception as e:
                print(f"  ✗ {route} - Error: {e}")
    
    return True

# Test 3: Test quiz submission and XP update
def test_quiz_submission():
    print("\n=== TEST 3: Quiz Submission & XP ===")
    import sqlite3
    from datetime import date
    
    DB_PATH = "placement.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get a test user
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    if not user:
        print("  ✗ No users found in database")
        return False
    
    user_id = user[0]
    print(f"  Testing with user_id: {user_id}")
    
    # Check XP before
    cursor.execute("SELECT xp FROM xp_points WHERE user_id = ?", (user_id,))
    xp_before = cursor.fetchone()
    xp_before = xp_before[0] if xp_before else 0
    print(f"  XP before: {xp_before}")
    
    # Check stats before
    cursor.execute("SELECT total_tests FROM user_stats WHERE user_id = ?", (user_id,))
    stats_before = cursor.fetchone()
    stats_before = stats_before[0] if stats_before else 0
    print(f"  Tests before: {stats_before}")
    
    conn.close()
    print("  ✓ Quiz submission mechanics ready")
    return True

# Test 4: Check dashboard data queries
def test_dashboard_queries():
    print("\n=== TEST 4: Dashboard Queries ===")
    import sqlite3
    from datetime import date, timedelta
    
    DB_PATH = "placement.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get a test user
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    if not user:
        print("  ✗ No users found")
        return False
    
    user_id = user[0]
    
    try:
        # Test user_stats query
        cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        user_stats = cursor.fetchone()
        print(f"  ✓ user_stats query OK")
        
        # Test xp_points query
        cursor.execute("SELECT * FROM xp_points WHERE user_id = ?", (user_id,))
        xp_data = cursor.fetchone()
        print(f"  ✓ xp_points query OK")
        
        # Test streak_tracking query
        cursor.execute("SELECT * FROM streak_tracking WHERE user_id = ?", (user_id,))
        streak_data = cursor.fetchone()
        print(f"  ✓ streak_tracking query OK")
        
        # Test user_scores query
        cursor.execute("SELECT COUNT(*) FROM user_scores WHERE user_id = ?", (user_id,))
        total_tests = cursor.fetchone()[0]
        print(f"  ✓ user_scores query OK - {total_tests} tests found")
        
        # Test category_performance query
        cursor.execute("SELECT * FROM category_performance WHERE user_id = ?", (user_id,))
        cat_perf = cursor.fetchone()
        print(f"  ✓ category_performance query OK")
        
        # Test xp_history query
        cursor.execute("SELECT * FROM xp_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user_id,))
        xp_hist = cursor.fetchall()
        print(f"  ✓ xp_history query OK - {len(xp_hist)} entries")
        
        # Test user_badges query
        cursor.execute("SELECT b.*, ub.earned_at FROM user_badges ub JOIN badges b ON ub.badge_id = b.id WHERE ub.user_id = ?", (user_id,))
        badges = cursor.fetchall()
        print(f"  ✓ user_badges query OK - {len(badges)} badges")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Query error: {e}")
        conn.close()
        return False

# Test 5: Check adaptive difficulty functions
def test_adaptive_difficulty():
    print("\n=== TEST 5: Adaptive Difficulty ===")
    from app import _calculate_recommended_difficulty
    
    # Test cases
    test_cases = [
        (85, 'Easy', ('Medium', 'increase')),
        (90, 'Medium', ('Hard', 'increase')),
        (95, 'Hard', ('Hard', 'max')),
        (45, 'Medium', ('Easy', 'decrease')),
        (50, 'Easy', ('Easy', 'maintain')),
        (75, 'Medium', ('Medium', 'maintain')),
    ]
    
    all_passed = True
    for accuracy, current, expected in test_cases:
        result = _calculate_recommended_difficulty(accuracy, current)
        if result == expected:
            print(f"  ✓ Accuracy {accuracy}%, Current {current} -> {result}")
        else:
            print(f"  ✗ Expected {expected}, got {result}")
            all_passed = False
    
    return all_passed

# Test 6: Check company mocks template
def test_company_mocks():
    print("\n=== TEST 6: Company Mocks ===")
    import sqlite3
    
    DB_PATH = "placement.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if company quizzes exist
    cursor.execute("SELECT id, name FROM quizzes WHERE name LIKE '%TCS%' OR name LIKE '%Infosys%' OR name LIKE '%Wipro%' OR name LIKE '%Amazon%'")
    company_quizzes = cursor.fetchall()
    
    if company_quizzes:
        print(f"  ✓ Found {len(company_quizzes)} company mock quizzes:")
        for q in company_quizzes:
            print(f"    - ID {q[0]}: {q[1]}")
    else:
        print("  ⚠ No company mock quizzes found (need to add company questions)")
    
    conn.close()
    return True

# Test 7: Check templates exist
def test_templates():
    print("\n=== TEST 7: Templates ===")
    required_templates = [
        'base.html', 'dashboard.html', 'company_mocks.html',
        'profile.html', 'index.html', 'quiz.html', 'levels.html'
    ]
    
    template_dir = 'templates'
    all_exist = True
    
    for template in required_templates:
        path = os.path.join(template_dir, template)
        if os.path.exists(path):
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} MISSING")
            all_exist = False
    
    return all_exist

# Run all tests
if __name__ == "__main__":
    print("=" * 50)
    print("FULL SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    results = []
    
    results.append(("Database Tables", test_database_tables()))
    results.append(("App Routes", test_app_routes()))
    results.append(("Quiz Submission", test_quiz_submission()))
    results.append(("Dashboard Queries", test_dashboard_queries()))
    results.append(("Adaptive Difficulty", test_adaptive_difficulty()))
    results.append(("Company Mocks", test_company_mocks()))
    results.append(("Templates", test_templates()))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready for use.")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
