import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('SELECT id, name FROM quizzes WHERE name LIKE "%Pattern%" OR name="Mock Test"')
quizzes = cursor.fetchall()
print('Quizzes:', quizzes)

cursor.execute('SELECT quiz_id, COUNT(*) FROM questions GROUP BY quiz_id')
questions = cursor.fetchall()
print('Questions by quiz:', questions)

cursor.execute('SELECT id, name FROM quizzes')
all_quizzes = cursor.fetchall()
print('All quizzes:', all_quizzes)

conn.close()
