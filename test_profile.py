import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("=" * 60)
print("PROFILE PAGE TEST")
print("=" * 60)

# Test 1: Register a new user
print("\n[1] Registering a new test user...")
register_data = {
    "email": "profiletest@test.com",
    "username": "profiletester",
    "age": "25",
    "gender": "Male",
    "mobile_number": "9876543210",
    "password": "Test@123",
    "confirm_password": "Test@123"
}

response = session.post(f"{BASE_URL}/register", data=register_data)
if response.status_code == 200:
    if "logged in successfully" in response.text or "register" in response.url:
        print("✅ Registration successful")
    else:
        print("⚠️  Registration page shown (might need to login separately)")
else:
    print(f"❌ Registration failed: {response.status_code}")

# Test 2: Login
print("\n[2] Logging in...")
login_data = {
    "email": "profiletest@test.com",
    "password": "Test@123"
}

response = session.post(f"{BASE_URL}/login", data=login_data)
if "login" not in response.url:
    print("✅ Login successful")
else:
    print(f"⚠️  Still on login page")

# Test 3: Complete a quiz
print("\n[3] Completing a quiz to generate stats...")
# Get quiz page to find questions
response = session.get(f"{BASE_URL}/quiz/Aptitude/Easy")
if "question" in response.text.lower():
    print("✅ Quiz page loaded")
    
    # Submit quiz answers (all correct answer is option1)
    quiz_data = {}
    soup = BeautifulSoup(response.text, 'html.parser')
    inputs = soup.find_all('input', type='radio')
    
    # Extract question IDs
    for inp in inputs:
        name = inp.get('name')
        if name and name.startswith('question_'):
            quiz_data[name] = inp.get('value')
    
    if quiz_data:
        print(f"   Found {len(set(key.split('_')[1] for key in quiz_data))} questions to answer")
    
    # Submit quiz
    submit_response = session.post(f"{BASE_URL}/api/submit-quiz", 
                                   json={
                                       "category": "Aptitude",
                                       "level": "Easy",
                                       "answers": quiz_data
                                   })
    if submit_response.status_code == 200:
        print("✅ Quiz submitted")
    else:
        print(f"⚠️  Quiz submission returned: {submit_response.status_code}")
else:
    print("⚠️  Quiz page not loaded properly")

# Test 4: Access Profile Page
print("\n[4] Accessing Profile Page...")
response = session.get(f"{BASE_URL}/profile")

if response.status_code == 200:
    print("✅ Profile page loaded successfully")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for key elements
    checks = {
        "Username": soup.find(text=lambda t: t and "profiletester" in t),
        "Email": soup.find(text=lambda t: t and "profiletest@test.com" in t),
        "Mobile Number": soup.find(text=lambda t: t and "9876543210" in t),
        "Gender": soup.find(text=lambda t: t and "Male" in t),
        "Profile Header": soup.find('div', class_='profile-header'),
        "Statistics Cards": soup.find_all('div', class_='stat-card'),
        "Personal Info Cards": soup.find_all('div', class_='info-card'),
        "Recent Quizzes Section": soup.find(text=lambda t: t and "Recent Quiz Attempts" in (t if t else "")),
    }
    
    print("\n   [Profile Elements Check]")
    for element, found in checks.items():
        if element in ["Statistics Cards", "Personal Info Cards"]:
            if found and len(found) > 0:
                print(f"   ✅ {element}: {len(found)} found")
            else:
                print(f"   ❌ {element}: Not found")
        else:
            if found:
                print(f"   ✅ {element}: Found")
            else:
                print(f"   ⚠️  {element}: Not found")
    
    # Extract and display profile data
    print("\n   [Profile Data Display]")
    
    # Check for username
    if soup.find(text=lambda t: t and "profiletester" in str(t)):
        print(f"   ✅ Username displayed: profiletester")
    
    # Check for stat values
    stat_values = soup.find_all('div', class_='stat-value')
    if stat_values:
        print(f"   ✅ Statistics displayed ({len(stat_values)} stats shown)")
    
    # Check for recent quizzes
    quiz_items = soup.find_all('div', class_='quiz-item')
    if quiz_items:
        print(f"   ✅ Recent quizzes shown ({len(quiz_items)} quizzes)")
    else:
        print(f"   ⚠️  No recent quizzes displayed (might be expected if quiz data not saved)")

else:
    print(f"❌ Profile page failed: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
