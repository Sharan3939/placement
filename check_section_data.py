import sqlite3
DB_PATH = 'placement.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check company_mock_sections
print('=== company_mock_sections ===')
cursor.execute("SELECT * FROM company_mock_sections")
sections = cursor.fetchall()
print(f'Rows: {len(sections)}')
for s in sections:
    print(s)

# Check company_coding_questions
print('\n=== company_coding_questions ===')
cursor.execute("SELECT * FROM company_coding_questions")
coding = cursor.fetchall()
print(f'Rows: {len(coding)}')
for c in coding:
    print(c)

conn.close()
