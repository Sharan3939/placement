import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

questions = [
    ("What is 20% of 150?", "20", "25", "30", "35", "30"),
    ("What is 5 + 7?", "10", "11", "12", "13", "12"),
    ("Which is prime?", "4", "6", "7", "8", "7")
]

cursor.executemany("""
INSERT INTO mock_questions
(question, option1, option2, option3, option4, correct_answer)
VALUES (?, ?, ?, ?, ?, ?)
""", questions)

conn.commit()
conn.close()

print("Questions Added Successfully")