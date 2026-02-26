import sqlite3

DB_PATH = 'placement.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# Check company_mock_sections table
print("\n--- Checking company_mock_sections ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_mock_sections'")
if cursor.fetchone():
    cursor.execute("SELECT * FROM company_mock_sections LIMIT 5")
    print("company_mock_sections exists")
else:
    print("company_mock_sections DOES NOT EXIST")

# Check company_coding_questions table  
print("\n--- Checking company_coding_questions ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_coding_questions'")
if cursor.fetchone():
    print("company_coding_questions exists")
else:
    print("company_coding_questions DOES NOT EXIST")

conn.close()
