import sqlite3
DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clean up duplicate sections
print("Cleaning duplicates...")

# Delete all and re-insert fresh
cursor.execute("DELETE FROM company_mock_sections")
cursor.execute("DELETE FROM company_coding_questions")
conn.commit()

# Insert correct sections (4 per company)
companies = [(5, 'TCS'), (6, 'Infosys'), (7, 'Wipro'), (8, 'Amazon')]

sections = []
for company_id, name in companies:
    # Aptitude: 8 questions (3 easy, 3 medium, 2 hard) from quiz 1
    # Reasoning: 5 questions (2 easy, 2 medium, 1 hard) from quiz 9
    # Verbal: 4 questions (2 easy, 1 medium, 1 hard) from quiz 10
    # Technical: 5 questions (2 easy, 2 medium, 1 hard) from quiz 3
    sections.extend([
        (company_id, 'Aptitude', 1, 8, 3, 3, 2),
        (company_id, 'Reasoning', 9, 5, 2, 2, 1),
        (company_id, 'Verbal', 10, 4, 2, 1, 1),
        (company_id, 'Technical', 3, 5, 2, 2, 1),
    ])

cursor.executemany("""INSERT INTO company_mock_sections 
    (company_quiz_id, section_name, source_quiz_id, num_questions, difficulty_easy, difficulty_medium, difficulty_hard)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", sections)

# Insert coding questions (3 per company)
coding_qs = []
for company_id, name in companies:
    coding_qs.extend([
        (company_id, 'Two Sum', 'Find indices of two numbers that add up to target', 
         'First line: n\nSecond line: n integers\nThird line: target',
         'Print indices (0-based) space-separated', '2 <= n <= 1000',
         '[{"input": "4\\n2 7 11 15\\n9", "output": "0 1"}]', 'Easy',
         'def two_sum(nums, target):\n    pass'),
        (company_id, 'Prime Check', 'Check if a number is prime',
         'A single integer n', "Print 'Yes' if prime, 'No' otherwise", '1 <= n <= 10^9',
         '[{"input": "17", "output": "Yes"}]', 'Medium',
         'def is_prime(n):\n    pass'),
        (company_id, 'Fibonacci Sum', 'Find sum of first n Fibonacci numbers',
         'A single integer n', 'Print sum of first n Fibonacci numbers', '1 <= n <= 30',
         '[{"input": "5", "output": "7"}]', 'Hard',
         'def fib_sum(n):\n    pass'),
    ])

cursor.executemany("""INSERT INTO company_coding_questions
    (company_quiz_id, title, description, input_format, output_format, constraints, test_cases, difficulty, starter_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", coding_qs)

conn.commit()

# Verify
cursor.execute("SELECT company_quiz_id, section_name, num_questions FROM company_mock_sections ORDER BY company_quiz_id, section_name")
print("\n=== Sections ===")
for row in cursor.fetchall():
    print(f"Company {row[0]}: {row[1]} = {row[2]} questions")

cursor.execute("SELECT company_quiz_id, COUNT(*) FROM company_coding_questions GROUP BY company_quiz_id")
print("\n=== Coding Questions ===")
for row in cursor.fetchall():
    print(f"Company {row[0]}: {row[1]} questions")

conn.close()
print("\n✅ Database cleaned and fixed!")
