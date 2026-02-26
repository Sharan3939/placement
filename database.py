import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = "placement.db"

def init_db():
    """Initialize database with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables (for fresh setup)
    cursor.execute("DROP TABLE IF EXISTS quiz_responses")
    cursor.execute("DROP TABLE IF EXISTS questions")
    cursor.execute("DROP TABLE IF EXISTS quizzes")
    cursor.execute("DROP TABLE IF EXISTS user_badges")
    cursor.execute("DROP TABLE IF EXISTS badges")
    cursor.execute("DROP TABLE IF EXISTS daily_activity")
    cursor.execute("DROP TABLE IF EXISTS coding_submissions")
    cursor.execute("DROP TABLE IF EXISTS coding_problems")
    cursor.execute("DROP TABLE IF EXISTS bookmarks")
    cursor.execute("DROP TABLE IF EXISTS xp_points")
    cursor.execute("DROP TABLE IF EXISTS user_roles")
    cursor.execute("DROP TABLE IF EXISTS user_scores")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # ==================== CORE TABLES ====================
    
    # Create users table for authentication
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        mobile_number TEXT,
        gender TEXT,
        age INTEGER,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create user roles table (for role-based access)
    cursor.execute("""
    CREATE TABLE user_roles (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create XP points table for gamification
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS xp_points (
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
    """)
    
    # Create user_stats table for detailed performance tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        total_tests INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        total_questions INTEGER DEFAULT 0,
        average_accuracy REAL DEFAULT 0,
        strongest_category TEXT,
        weakest_category TEXT,
        total_time_spent INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_test_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create category_performance table for adaptive difficulty
    cursor.execute("""
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
        UNIQUE(user_id, quiz_id)
    )
    """)
    
    # Create xp_history table for XP transactions
    cursor.execute("""
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
    """)
    
    # Create streak_tracking table for daily streaks
    cursor.execute("""
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create badges table
    cursor.execute("""
    CREATE TABLE badges (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT,
        xp_reward INTEGER DEFAULT 0,
        category TEXT,
        requirement_type TEXT,
        requirement_value INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create user badges table
    cursor.execute("""
    CREATE TABLE user_badges (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        badge_id INTEGER NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (badge_id) REFERENCES badges(id),
        UNIQUE(user_id, badge_id)
    )
    """)
    
    # Create bookmarks table
    cursor.execute("""
    CREATE TABLE bookmarks (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id),
        UNIQUE(user_id, question_id)
    )
    """)
    
    # Create coding problems table
    cursor.execute("""
    CREATE TABLE coding_problems (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        input_format TEXT,
        output_format TEXT,
        constraints TEXT,
        test_cases TEXT,
        difficulty TEXT DEFAULT 'Easy',
        starter_code TEXT,
        solution_code TEXT,
        xp_reward INTEGER DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create problem solutions table for multi-language solutions
    cursor.execute("""
    CREATE TABLE problem_solutions (
        id INTEGER PRIMARY KEY,
        problem_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        code TEXT NOT NULL,
        time_complexity TEXT,
        space_complexity TEXT,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES coding_problems(id)
    )
    """)
    
    # Create coding submissions table
    cursor.execute("""
    CREATE TABLE coding_submissions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        code TEXT,
        language TEXT,
        status TEXT DEFAULT 'pending',
        runtime TEXT,
        memory TEXT,
        test_results TEXT,
        score INTEGER DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (problem_id) REFERENCES coding_problems(id)
    )
    """)
    
    # Create daily activity table for streak tracking
    cursor.execute("""
    CREATE TABLE daily_activity (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        activity_date DATE NOT NULL,
        activity_type TEXT,
        xp_earned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, activity_date, activity_type)
    )
    """)
    
    # Create user scores table for leaderboard
    cursor.execute("""
    CREATE TABLE user_scores (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        difficulty TEXT,
        score INTEGER,
        total INTEGER,
        percentage REAL,
        time_taken INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    )
    """)
    
    # Create quizzes table
    cursor.execute("""
    CREATE TABLE quizzes (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        category TEXT,
        description TEXT
    )
    """)
    
    # Create questions table
    cursor.execute("""
    CREATE TABLE questions (
        id INTEGER PRIMARY KEY,
        quiz_id INTEGER,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        correct_answer TEXT,
        explanation TEXT,
        difficulty TEXT DEFAULT 'Easy',
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    )
    """)
    
    # Create quiz responses table (for tracking user answers)
    cursor.execute("""
    CREATE TABLE quiz_responses (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        quiz_id INTEGER,
        question_id INTEGER,
        user_answer TEXT,
        is_correct BOOLEAN,
        time_taken INTEGER,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    """)
    
    # ==================== INSERT DATA ====================
    
    # Insert quizzes
    quizzes = [
        ("Aptitude", "Quantitative Aptitude & Reasoning"),
        ("Coding", "Python & DataStructures"),
        ("Technical", "DBMS, OS & Networks"),
        ("Mock Test", "Full Length Mock Test"),
    ]
    
    for name, desc in quizzes:
        cursor.execute("INSERT INTO quizzes (name, category, description) VALUES (?, ?, ?)",
                      (name, name, desc))
    
    # Insert quizzes
    quizzes = [
        ("Aptitude", "Quantitative Aptitude & Reasoning"),
        ("Coding", "Python & DataStructures"),
        ("Technical", "DBMS, OS & Networks"),
        ("Mock Test", "Full Length Mock Test"),
    ]
    
    for name, desc in quizzes:
        cursor.execute("INSERT INTO quizzes (name, category, description) VALUES (?, ?, ?)",
                      (name, name, desc))
    
    # Insert Aptitude Questions with difficulty levels
    aptitude_qs = [
        # Easy (15 questions)
        (1, "What is 20% of 150?", "25", "30", "35", "40", "30", 
         "(Value / Total) × 100 = (30 / 150) × 100 = 20%", "Easy"),
        (1, "What is the average of 10, 20, 30, 40?", "20", "25", "30", "35", "25",
         "Average = (10 + 20 + 30 + 40) / 4 = 100 / 4 = 25", "Easy"),
        (1, "What is 15% of 200?", "25", "30", "35", "40", "30",
         "(15 / 100) × 200 = 30", "Easy"),
        (1, "If 5 apples cost $10, what is the cost of 1 apple?", "$1", "$2", "$3", "$4", "$2",
         "Cost of 1 apple = 10 / 5 = $2", "Easy"),
        (1, "What is the ratio of 4:8 in simplest form?", "1:2", "2:4", "4:8", "8:16", "1:2",
         "4:8 = 4÷4 : 8÷4 = 1:2", "Easy"),
        (1, "What is 25% of 80?", "15", "20", "25", "30", "20",
         "(25 / 100) × 80 = 20", "Easy"),
        (1, "If a dozen eggs cost $6, what is the cost of 18 eggs?", "$8", "$9", "$10", "$12", "$9",
         "Cost per egg = 6/12 = $0.5. 18 eggs = 18 × 0.5 = $9", "Easy"),
        (1, "What is the simple interest on $500 at 5% for 2 years?", "$50", "$40", "$60", "$70", "$50",
         "SI = (P × R × T) / 100 = (500 × 5 × 2) / 100 = $50", "Easy"),
        (1, "Which is greater: 3/4 or 4/5?", "3/4", "4/5", "Both equal", "Cannot determine", "4/5",
         "3/4 = 0.75, 4/5 = 0.8. So 4/5 is greater", "Easy"),
        (1, "If A:B = 2:3 and B:C = 3:4, find A:B:C", "2:3:4", "1:1.5:2", "2:3:4", "6:9:12", "2:3:4",
         "A:B = 2:3 and B:C = 3:4, so A:B:C = 2:3:4", "Easy"),
        (1, "What is 10% of 500?", "40", "50", "60", "70", "50",
         "(10 / 100) × 500 = 50", "Easy"),
        (1, "If 8 pens cost $16, what is the cost of 5 pens?", "$8", "$10", "$12", "$14", "$10",
         "Cost per pen = 16/8 = $2. 5 pens = 5 × 2 = $10", "Easy"),
        (1, "Find the average of 15, 25, 35, 45", "30", "25", "35", "40", "30",
         "Average = (15 + 25 + 35 + 45) / 4 = 120 / 4 = 30", "Easy"),
        (1, "What is the simplified form of 6:9?", "1:1.5", "2:3", "3:4", "4:6", "2:3",
         "6:9 = 6÷3 : 9÷3 = 2:3", "Easy"),
        (1, "What is 50% of 120?", "50", "60", "70", "80", "60",
         "(50 / 100) × 120 = 60", "Easy"),
        
        # Medium (15 questions)
        (1, "If a man walks 10 km in 2 hours, what is his speed?", "4 km/h", "5 km/h", "6 km/h", "7 km/h", "5 km/h",
         "Speed = Distance / Time = 10 / 2 = 5 km/h", "Medium"),
        (1, "A sells an item for $100 with 20% profit. What is the cost price?", "$80", "$60", "$70", "$90", "$80",
         "CP = SP / (1 + profit%) = 100 / 1.2 = 83.33 ≈ $80", "Medium"),
        (1, "If A can do a work in 10 days and B in 15 days, how long will they take together?", "6 days", "5 days", "8 days", "7 days", "6 days",
         "Combined rate = 1/10 + 1/15 = 5/30 = 1/6, so 6 days", "Medium"),
        (1, "What is the compound interest on $1000 at 10% p.a. for 2 years?", "$210", "$200", "$220", "$190", "$210",
         "CI = 1000(1.1)² - 1000 = 1210 - 1000 = $210", "Medium"),
        (1, "If 3 workers can build a wall in 6 days, how long will 2 workers take?", "9 days", "8 days", "10 days", "12 days", "9 days",
         "More workers = less time. 3×6 = 2×x, x = 9", "Medium"),
        (1, "A train travels at 60 km/h. How far does it travel in 3.5 hours?", "180 km", "190 km", "210 km", "220 km", "210 km",
         "Distance = Speed × Time = 60 × 3.5 = 210 km", "Medium"),
        (1, "If a discount of 20% is given on item costing $500, what is the final price?", "$300", "$350", "$400", "$450", "$400",
         "Discount = 500 × 20% = $100. Final price = 500 - 100 = $400", "Medium"),
        (1, "Two pipes fill a tank in 8 and 12 hours. Time to fill together?", "3.2 hours", "4.8 hours", "5 hours", "6 hours", "4.8 hours",
         "Combined rate = 1/8 + 1/12 = 5/24, Time = 24/5 = 4.8 hours", "Medium"),
        (1, "If the cost price is $50 and profit is 30%, what is selling price?", "$60", "$65", "$70", "$75", "$65",
         "SP = CP + Profit = 50 + (50 × 30%) = 50 + 15 = $65", "Medium"),
        (1, "A book's price increased from $20 to $25. What is the percentage increase?", "15%", "20%", "25%", "30%", "25%",
         "% increase = ((25-20)/20) × 100 = 25%", "Medium"),
        (1, "If a car travels 300 km in 5 hours, what is its speed?", "50 km/h", "60 km/h", "70 km/h", "80 km/h", "60 km/h",
         "Speed = Distance / Time = 300 / 5 = 60 km/h", "Medium"),
        (1, "What is 15% of $400?", "$50", "$60", "$70", "$80", "$60",
         "(15 / 100) × 400 = 60", "Medium"),
        (1, "If A:B = 3:5 and A = 12, what is B?", "15", "20", "25", "30", "20",
         "If A:B = 3:5 and A = 12, then 3/5 = 12/B, B = 20", "Medium"),
        (1, "A shopkeeper buys goods for $1000 and sells at 25% profit. SP is?", "$1200", "$1250", "$1300", "$1350", "$1250",
         "SP = CP + Profit = 1000 + (1000 × 25%) = 1000 + 250 = $1250", "Medium"),
        (1, "If 4 men can complete a job in 8 days, how many days will 6 men take?", "5.33 days", "6 days", "7 days", "8 days", "5.33 days",
         "Work is constant. 4×8 = 6×d, d = 32/6 = 5.33 days", "Medium"),
        
        # Hard (10 questions)
        (1, "A man buys apples at $5 each and sells at $8 each. If he makes $30 profit, how many apples did he buy?", "8", "10", "12", "15", "10",
         "Profit per apple = 8 - 5 = $3. Total profit = $30, so 30/3 = 10 apples", "Hard"),
        (1, "Three numbers are in ratio 2:3:4. If their sum is 180, find the largest number.", "60", "80", "100", "120", "80",
         "Let numbers be 2x, 3x, 4x. 2x+3x+4x=180, 9x=180, x=20. Largest = 4×20 = 80", "Hard"),
        (1, "A tank can be filled in 4 hours and emptied in 6 hours. If both opened simultaneously, how long to fill?", "12 hours", "10 hours", "8 hours", "15 hours", "12 hours",
         "Net rate = 1/4 - 1/6 = 3/12 - 2/12 = 1/12, so 12 hours", "Hard"),
        (1, "If x² + 1/x² = 10, then what is x + 1/x?", "√12", "√8", "√6", "2√3", "√12",
         "(x + 1/x)² = x² + 2 + 1/x² = 10 + 2 = 12, so x + 1/x = √12", "Hard"),
        (1, "In a group of 100 people, 40 speak English, 30 speak French, 20 speak both. How many speak neither?", "50", "45", "40", "35", "50",
         "Using sets: 40 + 30 - 20 = 50 speak at least one. 100 - 50 = 50 speak neither", "Hard"),
        (1, "A merchant bought goods for $2000 and sold at a loss of 15%. What is the selling price?", "$1600", "$1700", "$1800", "$1900", "$1700",
         "SP = CP - Loss = 2000 - (2000 × 15%) = 2000 - 300 = $1700", "Hard"),
        (1, "If 5 men and 4 women earn $1000 per day, and 2 men and 3 women earn $600 per day, find man's daily wage.", "$100", "$120", "$150", "$160", "$120",
         "5m + 4w = 1000 and 2m + 3w = 600. Solving: m = $120", "Hard"),
        (1, "A sum of money becomes 3 times in 15 years at simple interest. What is the rate?", "10%", "12.5%", "13.33%", "15%", "13.33%",
         "SI = 2P (since 3P - P = 2P). 2P = (P × R × 15)/100, R = 13.33%", "Hard"),
        (1, "In a race, A beats B by 100m. If A's speed is 10 m/s and B's is 8 m/s, find the race distance.", "400m", "500m", "600m", "700m", "500m",
         "When A finishes, B is 100m behind. If A runs d meters in d/10 seconds, B runs (d-100) = 8 × d/10, b = 500m", "Hard"),
        (1, "If x + y = 12 and xy = 32, find x² + y².", "80", "90", "100", "110", "80",
         "x² + y² = (x+y)² - 2xy = 144 - 64 = 80", "Hard"),
    ]
    
    # Insert Coding Questions with difficulty levels
    coding_qs = [
        # Easy (15 questions)
        (2, "What will be the output of: print(5 > 3)?", "True", "False", "5", "Error", "True",
         "5 > 3 is a boolean comparison that returns True", "Easy"),
        (2, "How do you create a function in Python?", "def func():", "function func():", "func():", "define func():", "def func():",
         "Python uses 'def' keyword to define functions", "Easy"),
        (2, "What is the output of: list(range(3))?", "[0, 1, 2]", "[1, 2, 3]", "[0, 1, 2, 3]", "[3]", "[0, 1, 2]",
         "range(3) generates 0, 1, 2. list() converts it to [0, 1, 2]", "Easy"),
        (2, "What will print(len('hello')) output?", "4", "5", "6", "Error", "5",
         "String 'hello' has 5 characters", "Easy"),
        (2, "What is the data type of 3.14?", "int", "float", "string", "bool", "float",
         "3.14 is a floating point number", "Easy"),
        (2, "How do you access the first element of a list?", "list[1]", "list[0]", "list.first", "list(0)", "list[0]",
         "Lists are 0-indexed, so first element is at index 0", "Easy"),
        (2, "What is the output of: 'hello'.upper()?", "'hello'", "'HELLO'", "'Hello'", "Error", "'HELLO'",
         "upper() method converts string to uppercase", "Easy"),
        (2, "What does the 'import' keyword do?", "Creates a variable", "Loads a module", "Defines a function", "Deletes data", "Loads a module",
         "'import' keyword is used to load/include modules in Python", "Easy"),
        (2, "What is a list in Python?", "Immutable collection", "Ordered mutable collection", "Fixed size array", "Dictionary", "Ordered mutable collection",
         "List is an ordered, mutable collection of elements", "Easy"),
        (2, "How do you check if a key exists in a dictionary?", "key in dict", "dict.has_key(key)", "dict[key]", "key.exists()", "key in dict",
         "'key in dict' returns True/False for key existence", "Easy"),
        (2, "What is the output of: 2 ** 3?", "6", "8", "5", "9", "8",
         "** is exponentiation operator. 2 ** 3 = 2 × 2 × 2 = 8", "Easy"),
        (2, "What does len() do?", "Deletes items", "Returns length", "Sorts items", "Clears memory", "Returns length",
         "len() returns the number of items in an object", "Easy"),
        (2, "What is the output of: int('42')?", "42.0", "42", "'42'", "Error", "42",
         "int() converts string to integer", "Easy"),
        (2, "What does str() function do?", "Deletes string", "Converts to string", "Compares strings", "Sorts strings", "Converts to string",
         "str() converts any data type to string", "Easy"),
        (2, "What is the output of: [1, 2] + [3, 4]?", "[1, 2, 3, 4]", "[1, 3, 2, 4]", "[3, 8]", "Error", "[1, 2, 3, 4]",
         "Using + operator concatenates two lists", "Easy"),
        
        # Medium (15 questions)
        (2, "Which data structure uses LIFO principle?", "Queue", "Stack", "Array", "Linked List", "Stack",
         "Stack is Last-In-First-Out (LIFO) data structure", "Medium"),
        (2, "What is the time complexity of binary search?", "O(n)", "O(log n)", "O(n²)", "O(1)", "O(log n)",
         "Binary search divides the array in half each time: O(log n)", "Medium"),
        (2, "How do you reverse a list in Python?", "list.reverse()", "list.reverse", "reverse(list)", "list[::-1]", "list.reverse()",
         "list.reverse() reverses the list in-place", "Medium"),
        (2, "What is the output of: 10 // 3?", "3", "3.33", "4", "3.0", "3",
         "// is floor division, returns integer division result", "Medium"),
        (2, "What does lambda do in Python?", "Creates a class", "Creates an anonymous function", "Loops through items", "Defines a variable", "Creates an anonymous function",
         "Lambda creates small anonymous functions without using def", "Medium"),
        (2, "What is the purpose of a 'for' loop?", "Conditional execution", "Repeating code", "Function definition", "Variable declaration", "Repeating code",
         "'for' loop is used to iterate through sequences", "Medium"),
        (2, "What does 'append()' do for a list?", "Removes first element", "Adds element at end", "Sorts the list", "Returns size", "Adds element at end",
         "append() method adds an element to the end of a list", "Medium"),
        (2, "What is the difference between '==' and 'is' in Python?", "No difference", "'==' compares values, 'is' compares identity", "'is' compares values", "Both compare identity", "'==' compares values, 'is' compares identity",
         "'==' checks value equality, 'is' checks object identity", "Medium"),
        (2, "What does 'try-except' block do?", "Loop through code", "Handles exceptions/errors", "Defines a function", "Creates a class", "Handles exceptions/errors",
         "'try-except' is used for error handling in Python", "Medium"),
        (2, "What is the output of: len([1, 2, 3, 4, 5])?", "4", "5", "6", "0", "5",
         "len() returns the number of elements in a list", "Medium"),
        (2, "What is recursion?", "Looping technique", "Function calling itself", "Creating loops", "Sorting method", "Function calling itself",
         "Recursion is when a function calls itself to solve smaller subproblems", "Medium"),
        (2, "What does the 'while' loop do?", "Executes once", "Repeats until condition is false", "Declares variables", "Imports modules", "Repeats until condition is false",
         "'while' loop repeats as long as condition is true", "Medium"),
        (2, "What is the output of: 2 + 3 * 4?", "20", "14", "14", "9", "14",
         "Multiplication has higher precedence than addition: 3*4=12, 2+12=14", "Medium"),
        (2, "What does 'del' keyword do?", "Defines variable", "Deletes variable/item", "Returns value", "Creates copy", "Deletes variable/item",
         "'del' keyword removes variables or elements from lists/dictionaries", "Medium"),
        (2, "What is the purpose of 'else' with 'for' loop?", "Completes the loop", "Executes when loop finishes normally", "Skips iterations", "Breaks loop", "Executes when loop finishes normally",
         "'else' in for loop executes after the loop completes normally (no break)", "Medium"),
        
        # Hard (10 questions)
        (2, "What is the time complexity of QuickSort in worst case?", "O(n)", "O(n log n)", "O(n²)", "O(log n)", "O(n²)",
         "QuickSort worst case is O(n²) when pivot is always smallest/largest", "Hard"),
        (2, "Which sorting algorithm is most efficient for linked lists?", "QuickSort", "MergeSort", "HeapSort", "BubbleSort", "MergeSort",
         "MergeSort is best for linked lists (O(n log n) and no random access needed)", "Hard"),
        (2, "What is the space complexity of recursive Fibonacci?", "O(1)", "O(n)", "O(n²)", "O(log n)", "O(n)",
         "Recursive Fibonacci uses O(n) call stack space", "Hard"),
        (2, "What does 'self' represent in a Python class?", "The class itself", "The current instance of the class", "The parent class", "A global variable", "The current instance of the class",
         "'self' refers to the current object instance in a class", "Hard"),
        (2, "Which method has O(1) average time for search in hash tables?", "Linear Search", "Binary Search", "Hash Table Lookup", "Tree Search", "Hash Table Lookup",
         "Hash tables provide O(1) average case lookup time", "Hard"),
        (2, "What is the worst-case space complexity of mergesort?", "O(n)", "O(log n)", "O(n log n)", "O(1)", "O(n)",
         "Mergesort requires O(n) additional space for merging arrays", "Hard"),
        (2, "What does a 'decorator' do in Python?", "Deletes functions", "Modifies function behavior", "Creates classes", "Sorts data", "Modifies function behavior",
         "Decorators wrap functions/methods to extend or modify their behavior", "Hard"),
        (2, "What is the difference between 'list' and 'tuple'?", "Both are same", "List is mutable, tuple is immutable", "Tuple is mutable", "List is immutable", "List is mutable, tuple is immutable",
         "Lists are changeable [1,2], tuples are fixed (1,2)", "Hard"),
        (2, "What is the output of: {1, 2, 2, 3}?", "[1, 2, 2, 3]", "{1, 2, 3}", "{1, 2, 2, 3}", "(1, 2, 2, 3)", "{1, 2, 3}",
         "Sets automatically remove duplicates, so {1, 2, 2, 3} becomes {1, 2, 3}", "Hard"),
        (2, "What is the time complexity of dictionary access in Python?", "O(n)", "O(log n)", "O(1) average", "O(n²)", "O(1) average",
         "Dictionary/hash table provides O(1) average case access time", "Hard"),
    ]
    
    # Insert Technical Questions with difficulty levels
    technical_qs = [
        # Easy (15 questions)
        (3, "What is Normalization?", "Reorganizing data", "Organizing data to reduce redundancy", "Sorting data", "Deleting data", "Organizing data to reduce redundancy",
         "Database Normalization is a process to organize data and reduce redundancy", "Easy"),
        (3, "Which key uniquely identifies a record?", "Foreign Key", "Primary Key", "Candidate Key", "Composite Key", "Primary Key",
         "Primary Key uniquely identifies each record in a table", "Easy"),
        (3, "Which protocol is used for secure web communication?", "HTTP", "FTP", "HTTPS", "SMTP", "HTTPS",
         "HTTPS is HTTP with SSL/TLS encryption for secure communication", "Easy"),
        (3, "What does TCP stand for?", "Transfer Control Protocol", "Transmission Control Protocol", "Transfer Code Protocol", "Transmission Code Protocol", "Transmission Control Protocol",
         "TCP = Transmission Control Protocol", "Easy"),
        (3, "What is the purpose of a firewall?", "To speed up internet", "To block unauthorized access", "To store data", "To manage files", "To block unauthorized access",
         "Firewall protects networks by blocking unauthorized access", "Easy"),
        (3, "What does RAM stand for?", "Read Access Memory", "Random Access Memory", "Run Application Mode", "Rapid Access Module", "Random Access Memory",
         "RAM = Random Access Memory", "Easy"),
        (3, "What is a database?", "Files in folders", "Organized collection of data", "Internet connection", "Computer program", "Organized collection of data",
         "Database is an organized collection of structured data", "Easy"),
        (3, "What does OS stand for?", "Operating System", "Online Service", "Output Stream", "Open Source", "Operating System",
         "OS = Operating System, manages hardware and software resources", "Easy"),
        (3, "What is DNS?", "Data Number System", "Domain Name System", "Direct Network Source", "Database Name Server", "Domain Name System",
         "DNS translates domain names to IP addresses", "Easy"),
        (3, "What is the purpose of IP address?", "Internet protection", "Identify devices on network", "Install program", "Internet provider", "Identify devices on network",
         "IP address identifies unique devices on a network", "Easy"),
        (3, "What does SQL stand for?", "Structured Query Language", "Standard Query List", "Strong Question Language", "System Query Logic", "Structured Query Language",
         "SQL = Structured Query Language for database operations", "Easy"),
        (3, "What is a table in a database?", "Data sheet", "Organized rows and columns of data", "Excel file", "Configuration file", "Organized rows and columns of data",
         "Table stores data in rows and columns format", "Easy"),
        (3, "What does URL stand for?", "Universal Resource Locator", "Uniform Resource Locator", "Upper Resource Link", "Unique Resource Locator", "Uniform Resource Locator",
         "URL = Uniform Resource Locator identifies web resources", "Easy"),
        (3, "What is encryption?", "Data compression", "Hiding data with algorithms", "Data deletion", "Data organization", "Hiding data with algorithms",
         "Encryption converts data into unreadable format using algorithms", "Easy"),
        (3, "What is malware?", "Software damage", "Malicious software", "Memory warning", "Performance issue", "Malicious software",
         "Malware includes viruses, worms, trojans designed to harm systems", "Easy"),
        
        # Medium (15 questions)
        (3, "What does ACID stand for in DBMS?", "Accuracy, Consistency, Integration, Durability", "Atomicity, Consistency, Isolation, Durability", "All, Commit, Integrate, Delete", "Append, Control, Index, Data", "Atomicity, Consistency, Isolation, Durability",
         "ACID ensures reliable database transactions", "Medium"),
        (3, "What is an index in a database?", "Table layout", "A data structure to quickly locate data", "Column names", "Row numbers", "A data structure to quickly locate data",
         "Index speeds up data retrieval operations", "Medium"),
        (3, "Which query language is used in DBMS?", "Python", "Java", "SQL", "C++", "SQL",
         "SQL (Structured Query Language) is the standard for databases", "Medium"),
        (3, "What is the purpose of 'DISTINCT' in SQL?", "Delete records", "Sort records", "Remove duplicate records", "Join tables", "Remove duplicate records",
         "DISTINCT removes duplicate rows from query results", "Medium"),
        (3, "What is the difference between primary and foreign key?", "No difference", "PK is unique, FK creates relationships", "FK is unique, PK creates relationships", "Both are same", "PK is unique, FK creates relationships",
         "PK uniquely identifies records, FK links tables", "Medium"),
        (3, "What is a view in database?", "Visual representation", "Virtual table from query results", "Page layout", "Data export", "Virtual table from query results",
         "View is a virtual table created from a SELECT query", "Medium"),
        (3, "What are the layers of OSI model?", "3 layers", "5 layers", "7 layers", "10 layers", "7 layers",
         "OSI model has 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application", "Medium"),
        (3, "What is bandwidth?", "Width of band", "Data transfer rate", "Network cable", "Connection type", "Data transfer rate",
         "Bandwidth is the maximum data transfer rate in a network", "Medium"),
        (3, "What does HTTP stand for?", "Hypertext Transfer Protocol", "High Transfer Technology Protocol", "Home Text Transfer Protocol", "Hyper Technology Text Protocol", "Hypertext Transfer Protocol",
         "HTTP = Hypertext Transfer Protocol for web communication", "Medium"),
        (3, "What is a stored procedure?", "Backup storage", "Pre-written SQL code stored in database", "Data storage method", "Memory storage", "Pre-written SQL code stored in database",
         "Stored procedure is reusable SQL code stored in the database", "Medium"),
        (3, "What is the purpose of a trigger in database?", "To start database", "To automatically execute SQL statements on events", "To delete records", "To create tables", "To automatically execute SQL statements on events",
         "Trigger automatically executes when specific database events occur", "Medium"),
        (3, "What does UDP stand for?", "User Defined Protocol", "User Datagram Protocol", "Universal Data Protocol", "Unified Delivery Protocol", "User Datagram Protocol",
         "UDP = User Datagram Protocol, connectionless transport layer protocol", "Medium"),
        (3, "What is a transaction in database?", "Money exchange", "Unit of work that succeeds/fails completely", "Data backup", "Network connection", "Unit of work that succeeds/fails completely",
         "Transaction ensures all-or-nothing principle (ACID properties)", "Medium"),
        (3, "What is cache memory?", "Cache files", "Fast memory between CPU and RAM", "Disk storage", "Network memory", "Fast memory between CPU and RAM",
         "Cache stores frequently accessed data for quick retrieval", "Medium"),
        (3, "What does HTTPS use for encryption?", "MD5", "SSL/TLS", "Base64", "SHA256 only", "SSL/TLS",
         "HTTPS uses SSL (Secure Sockets Layer) or TLS (Transport Layer Security)", "Medium"),
        
        # Hard (10 questions)
        (3, "What are the different types of Normalization?", "1NF, 2NF, 3NF", "1NF, 2NF, 3NF, BCNF", "Only 3NF", "1NF, 2NF only", "1NF, 2NF, 3NF, BCNF",
         "Database normalization includes 1NF, 2NF, 3NF, and BCNF", "Hard"),
        (3, "What does BCNF stand for?", "Basic Codd Normal Form", "Boyce Codd Normal Form", "Binary Codd Normal Form", "Base Codd Normal Form", "Boyce Codd Normal Form",
         "BCNF is Boyce Codd Normal Form, stricter than 3NF", "Hard"),
        (3, "Which layer of OSI model handles routing?", "Data Link", "Transport", "Network", "Session", "Network",
         "Network layer (Layer 3) handles routing of packets", "Hard"),
        (3, "What is the difference between clustered and non-clustered index?", "Both are same", "Clustered has leaf pages, non-clustered doesn't", "Clustered sorts table data, non-clustered doesn't", "No performance difference", "Clustered sorts table data, non-clustered doesn't",
         "Clustered index defines physical order, non-clustered creates separate structure", "Hard"),
        (3, "What is the maximum number of candidate keys in a table?", "1", "2", "Zero or more", "Always 1", "Zero or more",
         "Candidate keys are all minimal superkeys, can be zero or more", "Hard"),
        (3, "What is a deadlock in DBMS?", "Database crash", "Two transactions waiting for each other indefinitely", "Slow query", "Memory issue", "Two transactions waiting for each other indefinitely",
         "Deadlock occurs when transactions wait indefinitely for each other to release locks", "Hard"),
        (3, "What is the difference between HTTP and HTTPS?", "Same protocol", "HTTPS is encrypted, HTTP is not", "HTTP is faster", "Only port differs", "HTTPS is encrypted, HTTP is not",
         "HTTPS adds SSL/TLS encryption layer over HTTP for security", "Hard"),
        (3, "What are the different types of database JOIN?", "Only INNER", "INNER, LEFT, RIGHT, FULL", "INNER, OUTER", "Only OUTER", "INNER, LEFT, RIGHT, FULL",
         "Main JOINs are INNER, LEFT OUTER, RIGHT OUTER, and FULL OUTER", "Hard"),
        (3, "What is serialization in databases?", "Data storage", "Executing transactions in sequence to avoid conflicts", "Sending data", "Compression", "Executing transactions in sequence to avoid conflicts",
         "Serialization ensures transactions execute without conflicts maintaining consistency", "Hard"),
        (3, "What is a subquery?", "Question about data", "Query within another query", "Backup query", "Partial query", "Query within another query",
         "Subquery (inner query) executes within main query providing results to outer query", "Hard"),
    ]
    
    # Insert all questions with difficulty
    cursor.executemany("INSERT INTO questions (quiz_id, question, option1, option2, option3, option4, correct_answer, explanation, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       aptitude_qs + coding_qs + technical_qs)
    
    # ==================== INSERT BADGES ====================
    badges = [
        ("First Quiz", "Complete your first quiz", "🎯", 10, "quiz", "first_quiz", 1),
        ("Quiz Starter", "Complete 5 quizzes", "⭐", 25, "quiz", "quizzes_completed", 5),
        ("Quiz Master", "Complete 10 quizzes", "🌟", 50, "quiz", "quizzes_completed", 10),
        ("Quiz Champion", "Complete 25 quizzes", "🏆", 100, "quiz", "quizzes_completed", 25),
        ("Perfect Score", "Score 100% in any quiz", "💯", 20, "accuracy", "perfect_score", 100),
        ("High Achiever", "Score above 80%", "🎖", 15, "accuracy", "accuracy_above", 80),
        ("Day 1", "Login for 1 day", "🔥", 5, "streak", "streak_days", 1),
        ("Week Warrior", "Maintain 7 day streak", "💪", 35, "streak", "streak_days", 7),
        ("Month Master", "Maintain 30 day streak", "👑", 100, "streak", "streak_days", 30),
        ("XP Beginner", "Earn 100 XP", "🌱", 10, "xp", "xp_earned", 100),
        ("XP Hunter", "Earn 500 XP", "🎯", 30, "xp", "xp_earned", 500),
        ("XP Champion", "Earn 1000 XP", "🏅", 60, "xp", "xp_earned", 1000),
        ("XP Legend", "Earn 5000 XP", "🏆", 150, "xp", "xp_earned", 5000),
        ("Coder", "Submit 1 code", "💻", 10, "coding", "submissions", 1),
        ("Code Runner", "Submit 10 codes", "⌨️", 30, "coding", "submissions", 10),
        ("Code Master", "Submit 50 codes", "🖥️", 75, "coding", "submissions", 50),
        ("Aptitude Ace", "Complete Aptitude quiz 5 times", "🧮", 25, "category", "category_completed", 5),
        ("Tech Pro", "Complete Technical quiz 5 times", "🔧", 25, "category", "category_completed", 5),
        ("Coding Pro", "Complete Coding quiz 5 times", "🐍", 25, "category", "category_completed", 5),
    ]
    
    cursor.executemany("INSERT INTO badges (name, description, icon, xp_reward, category, requirement_type, requirement_value) VALUES (?, ?, ?, ?, ?, ?, ?)", badges)
    
    # ==================== INSERT SAMPLE CODING PROBLEMS ====================
    coding_problems = [
        ("Two Sum", "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.", 
         "First line: n (number of elements)\nSecond line: n space-separated integers\nThird line: target value",
         "Print indices of two numbers that add up to target (0-based, space-separated)",
         "2 <= n <= 1000\n-10^9 <= nums[i] <= 10^9",
         '[{"input": "4\\n2 7 11 15\\n9", "output": "0 1"}, {"input": "5\\n3 2 4 6 9\\n11", "output": "2 3"}]',
         "Easy", "def two_sum(nums, target):\n    # Your code here\n    pass", None, 15),
        
        ("Palindrome Check", "Check if a given string is a palindrome (reads the same forwards and backwards).",
         "A single string s (length 1 to 100)",
         "Print 'Yes' if palindrome, 'No' otherwise",
         "1 <= len(s) <= 100",
         '[{"input": "racecar", "output": "Yes"}, {"input": "hello", "output": "No"}]',
         "Easy", "def is_palindrome(s):\n    # Your code here\n    pass", None, 10),
        
        ("FizzBuzz", "For numbers 1 to n, print 'Fizz' if divisible by 3, 'Buzz' if divisible by 5, 'FizzBuzz' if both, else the number.",
         "A single integer n (1 <= n <= 100)",
         "Print numbers 1 to n, one per line",
         "1 <= n <= 100",
         '[{"input": "15", "output": "1\\n2\\nFizz\\n4\\nBuzz\\nFizz\\n7\\n8\\nFizz\\nBuzz\\n11\\nFizz\\n13\\n14\\nFizzBuzz"}]',
         "Easy", "def fizzbuzz(n):\n    # Your code here\n    pass", None, 12),
        
        ("Reverse Array", "Reverse an array and print the elements space-separated.",
         "First line: n (number of elements)\nSecond line: n space-separated integers",
         "Print reversed array elements space-separated",
         "1 <= n <= 1000",
         '[{"input": "5\\n1 2 3 4 5", "output": "5 4 3 2 1"}]',
         "Easy", "def reverse_array(arr):\n    # Your code here\n    pass", None, 10),
        
        ("Maximum Element", "Find the maximum element in an array.",
         "First line: n (number of elements)\nSecond line: n space-separated integers",
         "Print the maximum element",
         "1 <= n <= 100",
         '[{"input": "5\\n3 7 2 9 1", "output": "9"}]',
         "Easy", "def max_element(arr):\n    # Your code here\n    pass", None, 10),
        
        ("Sum of Array", "Calculate and print the sum of all elements in an array.",
         "First line: n (number of elements)\nSecond line: n space-separated integers",
         "Print the sum",
         "1 <= n <= 1000\n-10^6 <= arr[i] <= 10^6",
         '[{"input": "4\\n1 2 3 4", "output": "10"}]',
         "Easy", "def sum_array(arr):\n    # Your code here\n    pass", None, 8),
        
        ("Prime Number", "Check if a given number is prime.",
         "A single integer n (1 <= n <= 10^9)",
         "Print 'Yes' if prime, 'No' otherwise",
         "1 <= n <= 10^9",
         '[{"input": "17", "output": "Yes"}, {"input": "12", "output": "No"}]',
         "Medium", "def is_prime(n):\n    # Your code here\n    pass", None, 15),
        
        ("Fibonacci Series", "Print first n Fibonacci numbers.",
         "A single integer n (1 <= n <= 30)",
         "Print first n Fibonacci numbers space-separated",
         "1 <= n <= 30",
         '[{"input": "10", "output": "0 1 1 2 3 5 8 13 21 34"}]',
         "Medium", "def fibonacci(n):\n    # Your code here\n    pass", None, 15),
        
        ("Bubble Sort", "Sort an array using bubble sort and print sorted array.",
         "First line: n\nSecond line: n space-separated integers",
         "Print sorted array space-separated",
         "1 <= n <= 100",
         '[{"input": "5\\n5 2 8 1 9", "output": "1 2 5 8 9"}]',
         "Medium", "def bubble_sort(arr):\n    # Your code here\n    pass", None, 20),
    ]
    
    cursor.executemany("""INSERT INTO coding_problems 
        (title, description, input_format, output_format, constraints, test_cases, difficulty, starter_code, solution_code, xp_reward) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", coding_problems)
    
    # Create default admin user (password: admin123)
    from werkzeug.security import generate_password_hash
    admin_password = generate_password_hash("admin123")
    cursor.execute("""INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)""",
                   ("admin@placement.com", "admin", admin_password, "admin"))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
