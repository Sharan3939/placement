"""
Phase 3: Company-wise Mock Tests
Add TCS, Infosys, Wipro, Amazon pattern mock tests
"""

import sqlite3

DB_PATH = 'placement.db'

def add_company_mocks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== Adding Company Mock Tests ===\n")
    
    # Company mock quizzes
    company_quizzes = [
        ('TCS Pattern', 'TCS Fresher Hiring Pattern - Numerical, Verbal, Coding'),
        ('Infosys Pattern', 'Infosys Fresher Hiring Pattern - Aptitude, Coding'),
        ('Wipro Pattern', 'Wipro Fresher Hiring Pattern - Aptitude, Technical'),
        ('Amazon Pattern', 'Amazon SDE Hiring Pattern - Logical, Technical, Coding'),
    ]
    
    for name, desc in company_quizzes:
        cursor.execute("SELECT id FROM quizzes WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            quiz_id = existing[0]
            print(f"'{name}' already exists with ID: {quiz_id}")
        else:
            cursor.execute("INSERT INTO quizzes (name, description) VALUES (?, ?)", (name, desc))
            quiz_id = cursor.lastrowid
            print(f"Added '{name}' with ID: {quiz_id}")
    
    conn.commit()
    
    # Get quiz IDs
    cursor.execute("SELECT id, name FROM quizzes WHERE name LIKE '%Pattern%'")
    company_quiz_ids = {q[1]: q[0] for q in cursor.fetchall()}
    
    print(f"\nCompany Quiz IDs: {company_quiz_ids}")
    
    # Sample questions for each company
    # TCS Pattern Questions (quiz_id from company_quiz_ids)
    tcs_questions = [
        # Easy
        (company_quiz_ids.get('TCS Pattern'), "What is 15% of 200?", "25", "30", "35", "40", "30", "Easy", "Simple percentage calculation: 15/100 * 200 = 30"),
        (company_quiz_ids.get('TCS Pattern'), "If a train travels 60 km in 1 hour, how far will it travel in 5 hours?", "250 km", "300 km", "200 km", "350 km", "300 km", "Easy", "Distance = Speed × Time = 60 × 5 = 300 km"),
        (company_quiz_ids.get('TCS Pattern'), "Find the odd one out: Apple, Mango, Carrot, Banana", "Apple", "Mango", "Carrot", "Banana", "Carrot", "Easy", "Carrot is a vegetable, others are fruits"),
        
        # Medium
        (company_quiz_ids.get('TCS Pattern'), "A person buys an article for Rs. 100 and sells it for Rs. 120. What is the profit percentage?", "20%", "15%", "25%", "10%", "20%", "Medium", "Profit = 20, Cost = 100, Profit% = 20/100 × 100 = 20%"),
        (company_quiz_ids.get('TCS Pattern'), "Complete the series: 2, 6, 12, 20, ?", "30", "28", "32", "26", "30", "Medium", "Differences: 4, 6, 8, 10. Next: 20+10=30"),
        (company_quiz_ids.get('TCS Pattern'), "If CLOUD is coded as DMPVE, how is RAIN coded?", "SBJO", "SBJO", "QBKO", "QCJP", "SBJO", "Medium", "Each letter shifted by +1: R→S, A→B, I→J, N→O"),
    ]
    
    # Infosys Questions
    infosys_questions = [
        (company_quiz_ids.get('Infosys Pattern'), "What is the square root of 144?", "10", "11", "12", "13", "12", "Easy", "12 × 12 = 144"),
        (company_quiz_ids.get('Infosys Pattern'), "If 2x + 5 = 15, find x", "5", "4", "6", "3", "5", "Easy", "2x = 10, x = 5"),
        (company_quiz_ids.get('Infosys Pattern'), "What comes next: A, C, E, G, ?", "I", "J", "K", "H", "I", "Easy", "Skipping one letter each time"),
        
        (company_quiz_ids.get('Infosys Pattern'), "A man is 4 times as old as his son. After 8 years, he will be 3 times as old. Find son's age.", "8 years", "6 years", "10 years", "12 years", "8 years", "Medium", "Let son's age = x, man = 4x. After 8 years: 4x+8 = 3(x+8)"),
    ]
    
    # Wipro Questions
    wipro_questions = [
        (company_quiz_ids.get('Wipro Pattern'), "Which is the largest planet?", "Earth", "Jupiter", "Mars", "Saturn", "Jupiter", "Easy", "Jupiter is the largest planet in our solar system"),
        (company_quiz_ids.get('Wipro Pattern'), "What is 25 × 4?", "100", "80", "120", "90", "100", "Easy", "Simple multiplication"),
        
        (company_quiz_ids.get('Wipro Pattern'), "In a certain code, SISTER is written as RHRSDQ. How is BROTHER written?", "AQNSGDQ", "AQNSGDQ", "BQNSGER", "CANSGDQ", "AQNSGDQ", "Medium", "Each letter shifted by -1: B→A, R→Q, O→N, T→S, H→G, E→D, R→Q"),
        (company_quiz_ids.get('Wipro Pattern'), "Find the average of 10, 20, 30, 40", "25", "30", "20", "35", "25", "Medium", "Sum = 100, Average = 100/4 = 25"),
    ]
    
    # Amazon Questions
    amazon_questions = [
        (company_quiz_ids.get('Amazon Pattern'), "How many bits make a byte?", "4", "8", "16", "2", "8", "Easy", "8 bits = 1 byte"),
        (company_quiz_ids.get('Amazon Pattern'), "What is 100 - 37?", "63", "73", "53", "43", "63", "Easy", "Simple subtraction"),
        
        (company_quiz_ids.get('Amazon Pattern'), "If LOGIC is coded as 50-40-20-15-25, how is BRAVE coded?", "35-50-15-5-20", "35-50-15-5-20", "30-45-10-2-22", "38-52-18-8-24", "35-50-15-5-20", "Medium", "Position in alphabet: B=2→35, R=18→50, A=1→15, V=22→5, E=5→20"),
        (company_quiz_ids.get('Amazon Pattern'), "Find the missing number: 1, 1, 2, 3, 5, 8, ?", "11", "13", "12", "14", "13", "Medium", "Fibonacci: Each number is sum of previous two"),
    ]
    
    # Insert all questions
    all_questions = tcs_questions + infosys_questions + wipro_questions + amazon_questions
    
    for q in all_questions:
        cursor.execute("""INSERT OR IGNORE INTO questions 
            (quiz_id, question, option1, option2, option3, option4, correct_answer, difficulty, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", q)
    
    conn.commit()
    
    # Count questions added
    for name, qid in company_quiz_ids.items():
        cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (qid,))
        count = cursor.fetchone()[0]
        print(f"{name}: {count} questions")
    
    conn.close()
    print("\n✅ Company Mock Tests Added Successfully!")


if __name__ == "__main__":
    add_company_mocks()
