"""
PHASE 1: Company Mock Database Migration - COMPLETE VERSION
============================================================
"""

import sqlite3

DB_PATH = 'placement.db'

def migrate_phase1():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== PHASE 1 Migration ===\n")
    
    # 1. Add Reasoning and Verbal quizzes
    quizzes_to_add = [
        (9, 'Reasoning', 'Reasoning', 'Logical Reasoning Questions'),
        (10, 'Verbal', 'Verbal', 'Verbal Ability Questions'),
    ]
    
    for quiz_id, name, category, desc in quizzes_to_add:
        cursor.execute("SELECT id FROM quizzes WHERE id = ?", (quiz_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO quizzes (id, name, category, description) VALUES (?, ?, ?, ?)",
                         (quiz_id, name, category, desc))
            print(f"Added quiz: {name} (ID: {quiz_id})")
        else:
            print(f"Quiz exists: {name} (ID: {quiz_id})")
    
    conn.commit()
    
    # 2. Add Reasoning questions if not exist
    cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = 9")
    reasoning_count = cursor.fetchone()[0]
    
    if reasoning_count == 0:
        reasoning_questions = [
            (9, "If ALL DOGS are ANIMALS, and SOME ANIMALS are CATS, which is definitely true?", 
             "All dogs are cats", "Some dogs are animals", "All animals are dogs", "No conclusion can be drawn", 
             "No conclusion can be drawn", "Syllogism - cannot make definite conclusion", "Easy"),
            (9, "Find the odd one out: 2, 6, 12, 20, 30", "6", "12", "20", "30", "6", 
             "Pattern: n²+n: 2(1+1), 6(2+1), 12(3+1), 20(4+1), 30(5+1). 6 doesn't fit", "Easy"),
            (9, "Complete: CAT : ACT :: DOG : ?", "DGO", "GOD", "ODG", "GDO", "GOD", 
             "First and last letters swapped: C(AT) → A(CT), D(OG) → G(OD)", "Easy"),
            (9, "If A=1, B=2, C=3, what is the value of CAB?", "6", "8", "9", "7", "6", 
             "C=3, A=1, B=2. Total = 3+1+2 = 6", "Easy"),
            (9, "Pointing to a man, a woman said 'His mother is the only daughter of my mother.' How is the woman related?",
             "Sister", "Mother", "Aunt", "Grandmother", "Mother", "Only daughter of her mother = herself", "Medium"),
            (9, "If 2=6, 3=12, 4=20, then 5=?", "25", "30", "35", "40", "30", 
             "Pattern: n × (n+1): 2×3=6, 3×4=12, 4×5=20, 5×6=30", "Medium"),
            (9, "In a certain code, SISTER is written as RHRSDQ. How is BROTHER coded?",
             "AQNSGDQ", "BQNSGER", "CANSGDQ", "CQNSGDQ", "AQNSGDQ", 
             "Each letter shifted by -1: B→A, R→Q, O→N, T→S, H→G, E→D, R→Q", "Medium"),
            (9, "Statement: All roses are flowers. Some flowers fade quickly.", 
             "Some roses fade quickly", "All roses eventually fade", "Both follow", "Neither follows", 
             "Neither follows", "No direct link between roses and fading", "Medium"),
            (9, "Find the next: A, C, F, J, ?", "M", "O", "N", "P", "O", 
             "Gaps: 1,2,3,4 letters. J+4=O", "Medium"),
            (9, "If a clock shows 3:15, what is the angle between hour and minute hands?",
             "0 degrees", "7.5 degrees", "15 degrees", "22.5 degrees", "7.5 degrees", 
             "Minute=90°, hour=97.5°. Diff=7.5°", "Hard"),
        ]
        cursor.executemany("""INSERT INTO questions (quiz_id, question, option1, option2, option3, option4, correct_answer, explanation, difficulty) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", reasoning_questions)
        print(f"Added {len(reasoning_questions)} reasoning questions")
    
    # 3. Add Verbal questions if not exist
    cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = 10")
    verbal_count = cursor.fetchone()[0]
    
    if verbal_count == 0:
        verbal_questions = [
            (10, "Choose the synonym of 'BENEVOLENT'", "Cruel", "Kind", "Angry", "Sad", "Kind", "Benevolent means well-meaning and kind", "Easy"),
            (10, "Choose the antonym of 'ARTIFICIAL'", "Natural", "Synthetic", "Fake", "Man-made", "Natural", "Artificial means man-made, natural is opposite", "Easy"),
            (10, "The cat ___ under the table.", "sat", "sit", "sits", "sitting", "sat", "Past tense of sit is sat", "Easy"),
            (10, "She is ___ honest person.", "a", "an", "the", "no article", "an", "Honest starts with vowel sound, use 'an'", "Easy"),
            (10, "Choose the correct spelling:", "Accomodate", "Accommodate", "Acommodate", "Acomodate", "Accommodate", "Accommodate has double 'c' and double 'm'", "Easy"),
            (10, "The manager and the employee ___ arrived.", "has", "have", "having", "had", "have", "Two subjects joined by 'and' take plural verb", "Medium"),
            (10, "Choose the correct sentence:", "He is taller than me", "He is taller than I", "He is more tall than me", "He is more taller than I", "He is taller than I", 
             "After 'than' use subject form (I) not object (me)", "Medium"),
            (10, "The teacher gave ___ test to ___ students.", "a, the", "the, a", "the, the", "a, a", "the, the", 
             "'the test' is specific, 'the students' refers to particular group", "Medium"),
            (10, "Identify: 'Life is a journey'", "Metaphor", "Simile", "Personification", "Hyperbole", "Metaphor", 
             "Direct comparison without like/as", "Medium"),
            (10, "Choose the correctly spelled word:", "Occurrence", "Ocurrence", "Occurrance", "Occurence", "Occurrence", "Correct spelling has double 'r' and 'e'", "Medium"),
        ]
        cursor.executemany("""INSERT INTO questions (quiz_id, question, option1, option2, option3, option4, correct_answer, explanation, difficulty) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", verbal_questions)
        print(f"Added {len(verbal_questions)} verbal questions")
    
    conn.commit()
    
    # 4. Create company_mock_sections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_mock_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_quiz_id INTEGER NOT NULL,
            section_name TEXT NOT NULL,
            source_quiz_id INTEGER NOT NULL,
            num_questions INTEGER NOT NULL,
            difficulty_easy INTEGER DEFAULT 3,
            difficulty_medium INTEGER DEFAULT 3,
            difficulty_hard INTEGER DEFAULT 2,
            FOREIGN KEY (company_quiz_id) REFERENCES quizzes(id),
            FOREIGN KEY (source_quiz_id) REFERENCES quizzes(id)
        )
    """)
    print("\nCreated company_mock_sections table")
    
    # 5. Create company_coding_questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_coding_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_quiz_id INTEGER NOT NULL,
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
            FOREIGN KEY (company_quiz_id) REFERENCES quizzes(id)
        )
    """)
    print("Created company_coding_questions table")
    
    conn.commit()
    
    # 6. Insert section configurations
    # TCS, Infosys, Wipro, Amazon all have: Aptitude(8), Reasoning(5), Verbal(4), Technical(5)
    # And 3 coding questions
    companies = [
        (5, 'TCS Pattern'),
        (6, 'Infosys Pattern'),
        (7, 'Wipro Pattern'),
        (8, 'Amazon Pattern'),
    ]
    
    for company_id, company_name in companies:
        sections = [
            (company_id, 'Aptitude', 1, 8, 3, 3, 2),
            (company_id, 'Reasoning', 9, 5, 2, 2, 1),
            (company_id, 'Verbal', 10, 4, 2, 1, 1),
            (company_id, 'Technical', 3, 5, 2, 2, 1),
        ]
        for sec in sections:
            cursor.execute("""INSERT OR IGNORE INTO company_mock_sections 
                (company_quiz_id, section_name, source_quiz_id, num_questions, difficulty_easy, difficulty_medium, difficulty_hard)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", sec)
    
    print(f"Added section configurations for {len(companies)} companies")
    conn.commit()
    
    # 7. Add sample coding questions for each company
    # One Easy, One Medium, One Hard for each company
    for company_id, company_name in companies:
        coding_qs = [
            (company_id, "Two Sum", "Find indices of two numbers that add up to target", 
             "First line: n\nSecond line: n integers\nThird line: target",
             "Print indices (0-based) space-separated", 
             "2 <= n <= 1000",
             '[{"input": "4\\n2 7 11 15\\n9", "output": "0 1"}]',
             "Easy", "def two_sum(nums, target):\n    pass"),
            
            (company_id, "Prime Check", "Check if a number is prime", 
             "A single integer n",
             "Print 'Yes' if prime, 'No' otherwise",
             "1 <= n <= 10^9",
             '[{"input": "17", "output": "Yes"}]',
             "Medium", "def is_prime(n):\n    pass"),
            
            (company_id, "Fibonacci Sum", "Find sum of first n Fibonacci numbers", 
             "A single integer n",
             "Print sum of first n Fibonacci numbers",
             "1 <= n <= 30",
             '[{"input": "5", "output": "7"}]',
             "Hard", "def fib_sum(n):\n    pass"),
        ]
        cursor.executemany("""INSERT INTO company_coding_questions 
            (company_quiz_id, title, description, input_format, output_format, constraints, test_cases, difficulty, starter_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", coding_qs)
    
    print(f"Added 3 coding questions per company")
    conn.commit()
    
    print("\n=== PHASE 1 Migration Complete ===")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM company_mock_sections")
    sections_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM company_coding_questions")
    coding_count = cursor.fetchone()[0]
    print(f"Sections configured: {sections_count}")
    print(f"Coding questions: {coding_count}")
    
    conn.close()

if __name__ == "__main__":
    migrate_phase1()
