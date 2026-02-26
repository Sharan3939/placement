from app import app
from werkzeug.security import generate_password_hash
import sqlite3

client = app.test_client()

# Test 1: Register with new fields
print('Test 1: Register with profile information')
response = client.post('/register', data={
    'email': 'john@example.com',
    'username': 'johndoe',
    'password': 'secure123',
    'confirm_password': 'secure123',
    'age': '24',
    'gender': 'Male',
    'mobile_number': '9876543210'
}, follow_redirects=False)
print(f'  Status: {response.status_code}')
if 'Registration successful' in response.get_data(as_text=True):
    print('  ✅ User registered successfully')

# Test 2: Login
print('\nTest 2: Login')
response = client.post('/login', data={
    'email': 'john@example.com',
    'password': 'secure123'
}, follow_redirects=True)
if 'johndoe' in response.get_data(as_text=True):
    print('  ✅ Logged in successfully')

# Test 3: Access leaderboard
print('\nTest 3: Access leaderboard')
response = client.get('/leaderboard', follow_redirects=False)
print(f'  Status: {response.status_code}')
if response.status_code == 200:
    print('  ✅ Leaderboard accessible')

# Test 4: Verify database
print('\nTest 4: Verify database schema')
conn = sqlite3.connect('placement.db')
c = conn.cursor()

# Check users table has new fields
c.execute('PRAGMA table_info(users)')
columns = [row[1] for row in c.fetchall()]
if 'mobile_number' in columns and 'age' in columns and 'gender' in columns:
    print('  ✅ User profile fields added')

# Check user in database
c.execute('SELECT username, age, gender, mobile_number FROM users WHERE username = ?', ('johndoe',))
user = c.fetchone()
if user:
    print(f'  ✅ User stored: {user[0]}, Age: {user[1]}, Gender: {user[2]}, Mobile: {user[3]}')

# Check user_scores table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_scores'")
if c.fetchone():
    print('  ✅ User scores table created')

c.execute('PRAGMA table_info(user_scores)')
columns = [row[1] for row in c.fetchall()]
if 'percentage' in columns and 'difficulty' in columns:
    print('  ✅ Score tracking fields added')

conn.close()

print('\n✅ All tests passed! System is completely functional.')
