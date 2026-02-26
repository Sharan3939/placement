import sqlite3
import random

DB_PATH = 'placement.db'

def test_get_company_mock_questions(company_quiz_id):
    """Test the get_company_mock_questions function logic"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    result = {
        'mcq_sections': [],
        'coding_questions': []
    }
    
    # Get section configurations
    cursor.execute("""SELECT section_name, source_quiz_id, num_questions, 
        difficulty_easy, difficulty_medium, difficulty_hard
        FROM company_mock_sections WHERE company_quiz_id = ?
        ORDER BY section_name""", (company_quiz_id,))
    sections = cursor.fetchall()
    
    print(f"Testing company_quiz_id={company_quiz_id}")
    print(f"Sections found: {len(sections)}")
    
    for section in sections:
        section_name = section[0]
        source_quiz_id = section[1]
        num_questions = section[2]
        easy_count = section[3]
        medium_count = section[4]
        hard_count = section[5]
        
        print(f"\n{section_name}: source={source_quiz_id}, total={num_questions}, easy={easy_count}, medium={medium_count}, hard={hard_count}")
        
        # Check available questions
        cursor.execute("SELECT difficulty, COUNT(*) FROM questions WHERE quiz_id=? GROUP BY difficulty", (source_quiz_id,))
        available = cursor.fetchall()
        print(f"  Available: {dict(available)}")
        
        section_questions = []
        
        # Fetch Easy questions
        if easy_count > 0:
            cursor.execute("""SELECT id, question FROM questions WHERE quiz_id = ? AND difficulty = 'Easy'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, easy_count))
            section_questions.extend(cursor.fetchall())
            print(f"  Got {len(section_questions)} easy questions")
        
        # Fetch Medium questions
        if medium_count > 0:
            cursor.execute("""SELECT id, question FROM questions WHERE quiz_id = ? AND difficulty = 'Medium'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, medium_count))
            section_questions.extend(cursor.fetchall())
            print(f"  Got {len(section_questions)} medium questions")
        
        # Fetch Hard questions
        if hard_count > 0:
            cursor.execute("""SELECT id, question FROM questions WHERE quiz_id = ? AND difficulty = 'Hard'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, hard_count))
            section_questions.extend(cursor.fetchall())
            print(f"  Got {len(section_questions)} hard questions")
        
        print(f"  Total fetched: {len(section_questions)}/{num_questions}")
        
        result['mcq_sections'].append({
            'name': section_name,
            'questions': section_questions
        })
    
    # Get coding questions
    cursor.execute("""SELECT id, title, difficulty FROM company_coding_questions WHERE company_quiz_id = ?
        ORDER BY CASE difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Hard' THEN 3 END""", 
        (company_quiz_id,))
    coding = cursor.fetchall()
    result['coding_questions'] = coding
    print(f"\nCoding questions: {len(coding)}")
    for c in coding:
        print(f"  - {c[1]} ({c[2]})")
    
    conn.close()
    
    # Summary
    total_mcq = sum(len(s['questions']) for s in result['mcq_sections'])
    print(f"\n=== SUMMARY ===")
    print(f"Total MCQs: {total_mcq}")
    print(f"Total Coding: {len(result['coding_questions'])}")
    print(f"Total Questions: {total_mcq + len(result['coding_questions'])}")
    
    return result

# Test for TCS (quiz_id=5)
test_get_company_mock_questions(5)
