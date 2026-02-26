import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check existing quizzes
cursor.execute("SELECT id, name FROM quizzes WHERE name LIKE '%Pattern%'")
quizzes = cursor.fetchall()
print("Company quizzes:", quizzes)

# Check questions per quiz
for q in quizzes:
    cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (q[0],))
    count = cursor.fetchone()[0]
    print(f"  {q[1]}: {count} questions")

conn.close()
