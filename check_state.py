import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for t in tables:
    print(f'  - {t[0]}')

# Check if company_mock_sections exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_mock_sections'")
if cursor.fetchone():
    print("\ncompany_mock_sections table EXISTS")
    cursor.execute("SELECT * FROM company_mock_sections")
    sections = cursor.fetchall()
    print(f"Sections: {sections}")
else:
    print("\ncompany_mock_sections table does NOT exist")

# Check if company_coding_questions exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_coding_questions'")
if cursor.fetchone():
    print("\ncompany_coding_questions table EXISTS")
else:
    print("\ncompany_coding_questions table does NOT exist")

# Check quiz IDs
cursor.execute("SELECT id, name FROM quizzes")
quizzes = cursor.fetchall()
print("\nQuizzes:")
for q in quizzes:
    print(f"  {q[0]}: {q[1]}")

conn.close()
