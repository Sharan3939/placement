import sqlite3
DB_PATH = 'placement.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all quizzes
print('=== All Quizzes ===')
cursor.execute("SELECT id, name FROM quizzes ORDER BY id")
for q in cursor.fetchall():
    print(f'{q[0]}: {q[1]}')

# Check questions per quiz
print('\n=== Questions per Quiz ===')
cursor.execute("""
    SELECT q.id, q.name, COUNT(qs.id) as question_count 
    FROM quizzes q 
    LEFT JOIN questions qs ON q.id = qs.quiz_id 
    GROUP BY q.id 
    ORDER BY q.id
""")
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} - {row[2]} questions')

# Check difficulty distribution in aptitude (quiz_id=1)
print('\n=== Aptitude (quiz_id=1) difficulty distribution ===')
cursor.execute("SELECT difficulty, COUNT(*) FROM questions WHERE quiz_id=1 GROUP BY difficulty")
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')

conn.close()
