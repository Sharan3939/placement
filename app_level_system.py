"""
Placement Preparation Website - Final Version
With XP, Badges, Dashboard, Adaptive Difficulty, Company Mocks, and Level System
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import json
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "placement_secret_2024"
DB_PATH = "placement.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

XP_REWARDS = {'Easy': 10, 'Medium': 20, 'Hard': 30}
BADGE_LEVELS = {'Bronze': 100, 'Silver': 500, 'Gold': 1000, 'Platinum': 2000}
STREAK_BONUS_XP = {7: 50, 14: 100, 30: 250, 60: 500, 90: 1000}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return render_template("login.html", error="Email and password required")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        mobile_number = request.form.get('mobile_number')
        gender = request.form.get('gender')
        age = request.form.get('age')
        
        if not all([email, username, password, confirm_password, mobile_number, gender, age]):
            return render_template("register.html", error="All fields are required")
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            return render_template("register.html", error="Mobile number must be 10 digits")
        try:
            age = int(age)
            if age < 15 or age > 70:
                return render_template("register.html", error="Age must be between 15 and 70")
        except ValueError:
            return render_template("register.html", error="Invalid age")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
        if cursor.fetchone():
            conn.close()
            return render_template("register.html", error="Email or username already exists")
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute("""INSERT INTO users (email, username, password, mobile_number, gender, age) 
               VALUES (?, ?, ?, ?, ?, ?)""", (email, username, hashed_password, mobile_number, gender, age))
            user_id = cursor.lastrowid
            
            today = date.today()
            cursor.execute("INSERT INTO xp_points (user_id, xp, level, daily_streak, last_active_date) VALUES (?, 0, 'Beginner', 0, ?)", (user_id, today))
            cursor.execute("INSERT INTO streak_tracking (user_id, current_streak, longest_streak, last_login_date, total_login_days) VALUES (?, 0, 0, ?, 0)", (user_id, today))
            cursor.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
            
            conn.commit()
            conn.close()
            return render_template("register.html", success="Registration successful! Please login.")
        except Exception as e:
            conn.close()
            return render_template("register.html", error=f"Registration failed: {str(e)}")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    return render_template("index.html", username=session.get('username'))

@app.route("/quiz/<category>")
@login_required
def quiz(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM quizzes WHERE name = ?", (category.title(),))
    quiz = cursor.fetchone()
    if not quiz:
        return "<h1>Quiz Not Found</h1>", 404
    cursor.execute("SELECT DISTINCT difficulty FROM questions WHERE quiz_id = ? ORDER BY difficulty", (quiz['id'],))
    levels = [row['difficulty'] for row in cursor.fetchall()]
    conn.close()
    return render_template("levels.html", category=category.capitalize(), quiz_id=quiz['id'], levels=levels)

@app.route("/quiz/<category>/<level>")
@login_required
def quiz_questions(category, level):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM quizzes WHERE name = ?", (category.title(),))
    quiz = cursor.fetchone()
    if not quiz:
        return "<h1>Quiz Not Found</h1>", 404
    if level not in ['Easy', 'Medium', 'Hard']:
        return "<h1>Invalid Difficulty Level</h1>", 400
    
    if category.title() == "Mock Test":
        cursor.execute("""SELECT id, question, option1, option2, option3, option4, quiz_id
        FROM questions WHERE quiz_id IN (1, 2, 3) AND difficulty = ? ORDER BY quiz_id, id""", (level,))
    else:
        cursor.execute("""SELECT id, question, option1, option2, option3, option4 
        FROM questions WHERE quiz_id = ? AND difficulty = ?""", (quiz['id'], level))
    questions = cursor.fetchall()
    conn.close()
    if not questions:
        return "<h1>No questions available for this level</h1>", 404
    return render_template("quiz.html", category=category.title(), quiz_id=quiz['id'], level=level, questions=questions)


# ==================== COMPANY MOCK FUNCTIONS ====================

def get_company_mock_questions(company_quiz_id, level=1):
    """
    Fetch company mock questions with difficulty based on level.
    Level 1: Easy heavy (60% Easy, 30% Medium, 10% Hard)
    Level 2: Balanced (30% Easy, 50% Medium, 20% Hard)
    Level 3: Hard heavy (10% Easy, 40% Medium, 50% Hard)
    """
    import random
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {
        'mcq_sections': [],
        'coding_questions': []
    }
    
    # Get section configurations
    cursor.execute("""SELECT section_name, source_quiz_id, num_questions, 
        difficulty_easy, difficulty_medium, difficulty_hard
        FROM company_mock_sections WHERE company_quiz_id = ?
        ORDER BY section_name""", (company_quiz_id,))
    sections = cursor.fetchall()
    
    # Difficulty ratios based on level
    level_ratios = {
        1: {'Easy': 0.6, 'Medium': 0.3, 'Hard': 0.1},
        2: {'Easy': 0.3, 'Medium': 0.5, 'Hard': 0.2},
        3: {'Easy': 0.1, 'Medium': 0.4, 'Hard': 0.5}
    }
    ratios = level_ratios.get(level, level_ratios[1])
    
    for section in sections:
        section_name = section['section_name']
        source_quiz_id = section['source_quiz_id']
        num_questions = section['num_questions']
        
        # Calculate counts based on ratios
        easy_count = max(1, int(num_questions * ratios['Easy']))
        medium_count = max(1, int(num_questions * ratios['Medium']))
        hard_count = num_questions - easy_count - medium_count
        if hard_count < 0:
            hard_count = 0
        
        section_questions = []
        
        # Fetch Easy questions
        if easy_count > 0:
            cursor.execute("""SELECT id, question, option1, option2, option3, option4, correct_answer, explanation
                FROM questions WHERE quiz_id = ? AND difficulty = 'Easy'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, easy_count))
            section_questions.extend(cursor.fetchall())
        
        # Fetch Medium questions
        if medium_count > 0:
            cursor.execute("""SELECT id, question, option1, option2, option3, option4, correct_answer, explanation
                FROM questions WHERE quiz_id = ? AND difficulty = 'Medium'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, medium_count))
            section_questions.extend(cursor.fetchall())
        
        # Fetch Hard questions
        if hard_count > 0:
            cursor.execute("""SELECT id, question, option1, option2, option3, option4, correct_answer, explanation
                FROM questions WHERE quiz_id = ? AND difficulty = 'Hard'
                ORDER BY RANDOM() LIMIT ?""", (source_quiz_id, hard_count))
            section_questions.extend(cursor.fetchall())
        
        # If not enough questions, fetch more
        if len(section_questions) < num_questions:
            remaining = num_questions - len(section_questions)
            existing_ids = [q['id'] for q in section_questions]
            if existing_ids:
                placeholders = ','.join(['?'] * len(existing_ids))
                cursor.execute(f"""SELECT id, question, option1, option2, option3, option4, correct_answer, explanation
                    FROM questions WHERE quiz_id = ? AND id NOT IN ({placeholders})
                    ORDER BY RANDOM() LIMIT ?""", (source_quiz_id,) + tuple(existing_ids) + (remaining,))
            else:
                cursor.execute("""SELECT id, question, option1, option2, option3, option4, correct_answer, explanation
                    FROM questions WHERE quiz_id = ? ORDER BY RANDOM() LIMIT ?""", 
                    (source_quiz_id, remaining))
            section_questions.extend(cursor.fetchall())
        
        result['mcq_sections'].append({
            'name': section_name,
            'questions': [dict(q) for q in section_questions]
        })
    
    # Get coding questions (1 Easy, 1 Medium, 1 Hard)
    cursor.execute("""SELECT id, title, description, input_format, output_format, 
        constraints, difficulty, starter_code
        FROM company_coding_questions WHERE company_quiz_id = ?
        ORDER BY CASE difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Hard' THEN 3 END""", 
        (company_quiz_id,))
    coding = cursor.fetchall()
    result['coding_questions'] = [dict(c) for c in coding]
    
    conn.close()
    return result


@app.route("/quiz/company/<company_name>")
@login_required
def company_mock_test(company_name):
    """Company mock test with level selection"""
    level = request.args.get('level', 1, type=int)
    if level not in [1, 2, 3]:
        level = 1
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    company_map = {
        'tcs': 'TCS Pattern',
        'infosys': 'Infosys Pattern',
        'wipro': 'Wipro Pattern',
        'amazon': 'Amazon Pattern'
    }
    
    quiz_name = company_map.get(company_name.lower())
    if not quiz_name:
        return "<h1>Company Not Found</h1>", 404
    
    cursor.execute("SELECT id, name FROM quizzes WHERE name = ?", (quiz_name,))
    quiz = cursor.fetchone()
    if not quiz:
        return "<h1>Quiz Not Found</h1>", 404
    
    # Check if level is unlocked
    user_id = session.get('user_id')
    cursor.execute("""SELECT unlocked FROM company_level_progress 
        WHERE user_id = ? AND company_name = ? AND level = ?""", 
        (user_id, company_name.upper(), level))
    level_check = cursor.fetchone()
    
    if level > 1 and (not level_check or not level_check['unlocked']):
        return "<h1>Level Locked</h1><p>Complete previous level to unlock this level.</p>", 403
    
    # Get questions with level-based difficulty
    questions_data = get_company_mock_questions(quiz['id'], level)
    
    conn.close()
    
    # Flatten all MCQ questions
    all_mcqs = []
    for section in questions_data['mcq_sections']:
        for q in section['questions']:
            q_copy = dict(q)
            q_copy['section'] = section['name']
            all_mcqs.append(q_copy)
    
    return render_template("company_mock_v2.html",
        company=quiz_name.replace(' Pattern', ''),
        quiz_id=quiz['id'],
        level=level,
        sections=questions_data['mcq_sections'],
        mcq_questions=all_mcqs,
        coding_questions=questions_data['coding_questions'],
        total_mcqs=len(all_mcqs),
        total_coding=len(questions_data['coding_questions']))


# ==================== LEVEL SYSTEM ====================

@app.route("/company-mocks")
@login_required
def company_mocks():
    """Company-wise mock tests page with level selection"""
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    companies = [
        ('TCS', 'TCS Pattern', 'tcs'),
        ('Infosys', 'Infosys Pattern', 'infosys'),
        ('Wipro', 'Wipro Pattern', 'wipro'),
        ('Amazon', 'Amazon Pattern', 'amazon')
    ]
    
    company_data = []
    for company_key, quiz_name, url_key in companies:
        # Ensure level progress rows exist
        for level in [1, 2, 3]:
            cursor.execute("""INSERT OR IGNORE INTO company_level_progress 
                (user_id, company_name, level, best_score, unlocked) VALUES (?, ?, ?, 0, ?)""",
                (user_id, company_key, level, 1 if level == 1 else 0))
        
        # Get level status
        cursor.execute("""SELECT level, best_score, unlocked FROM company_level_progress 
            WHERE user_id = ? AND company_name = ? ORDER BY level""", (user_id, company_key))
        levels = cursor.fetchall()
        
        # Calculate progress
        total_score = sum(l['best_score'] for l in levels)
        unlocked_count = sum(1 for l in levels if l['unlocked'])
        progress = int(total_score / (len(levels) * 100) * 100) if levels else 0
        
        company_data.append({
            'key': url_key,
            'name': company_key,
            'levels': [dict(l) for l in levels],
            'progress': progress,
            'unlocked_count': unlocked_count
        })
    
    conn.commit()
    conn.close()
    
    return render_template("company_mocks.html", companies=company_data)


@app.route("/company-progress/<company>")
@login_required
def company_progress(company):
    """Company progress dashboard"""
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    company_name = company.upper()
    cursor.execute("""SELECT level, best_score, unlocked FROM company_level_progress 
        WHERE user_id = ? AND company_name = ? ORDER BY level""", (user_id, company_name))
    levels = cursor.fetchall()
    
    if not levels:
        return redirect(url_for('company_mocks'))
    
    unlocked_levels = [l for l in levels if l['unlocked']]
    if unlocked_levels:
        avg_score = sum(l['best_score'] for l in unlocked_levels) / len(unlocked_levels)
    else:
        avg_score = 0
    
    progress_percentage = int(avg_score)
    
    conn.close()
    
    return render_template("company_progress.html",
        company=company_name,
        levels=[dict(l) for l in levels],
        progress_percentage=progress_percentage)


@app.route("/api/submit-quiz", methods=["POST"])
@login_required
def submit_quiz():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', {})
    difficulty = data.get('difficulty', 'Easy')
    user_id = session.get('user_id')
    level = data.get('level', 1)
    company_name = data.get('company_name', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    section_scores = {}
    section_total = {}
    
    score = 0
    total = 0
    results = []
    
    for q_id, user_answer in answers.items():
        section = 'Coding'
        actual_q_id = q_id
        
        if '_' in q_id and q_id.startswith('q'):
            parts = q_id.rsplit('_', 1)
            if parts[0].startswith('q'):
                try:
                    actual_q_id = int(parts[0][1:])
                    section = parts[1]
                except:
                    actual_q_id = q_id
        
        if str(q_id).startswith('code_'):
            section = 'Coding'
            actual_q_id = q_id
        
        total += 1
        
        if str(actual_q_id).startswith('q'):
            try:
                actual_q_id = int(str(actual_q_id)[1:])
            except:
                pass
        
        if isinstance(actual_q_id, int):
            cursor.execute("""SELECT question, correct_answer, explanation FROM questions WHERE id = ?""", (actual_q_id,))
            question_data = cursor.fetchone()
            if question_data:
                is_correct = user_answer == question_data['correct_answer']
                if is_correct:
                    score += 1
                    section_scores[section] = section_scores.get(section, 0) + 1
                section_total[section] = section_total.get(section, 0) + 1
                results.append({
                    'question': question_data['question'],
                    'user_answer': user_answer,
                    'correct_answer': question_data['correct_answer'],
                    'is_correct': is_correct,
                    'section': section
                })
        else:
            section_total['Coding'] = section_total.get('Coding', 0) + 1
    
    percentage = (score / total * 100) if total > 0 else 0
    
    section_breakdown = []
    for section in ['Aptitude', 'Reasoning', 'Verbal', 'Technical', 'Coding']:
        if section in section_total:
            s_score = section_scores.get(section, 0)
            s_total = section_total[section]
            s_pct = (s_score / s_total * 100) if s_total > 0 else 0
            section_breakdown.append({
                'name': section,
                'score': s_score,
                'total': s_total,
                'percentage': round(s_pct, 1)
            })
    
    readiness = percentage
    if readiness >= 80:
        readiness_status = "Interview Ready"
    elif readiness >= 60:
        readiness_status = "Almost Ready"
    elif readiness >= 40:
        readiness_status = "Needs Improvement"
    else:
        readiness_status = "Not Ready"
    
    xp_earned = XP_REWARDS.get(difficulty, 10)
    if percentage >= 90:
        xp_earned += 5
    elif percentage >= 70:
        xp_earned += 2
    
    # Save score
    try:
        cursor.execute("""INSERT INTO user_scores (user_id, quiz_id, difficulty, score, total, percentage)
        VALUES (?, ?, ?, ?, ?, ?)""", (user_id, quiz_id, difficulty, score, total, percentage))
        cursor.execute("UPDATE xp_points SET xp = xp + ?, total_quizzes = total_quizzes + 1 WHERE user_id = ?", (xp_earned, user_id))
        cursor.execute("""INSERT INTO xp_history (user_id, xp_amount, transaction_type, description, related_id)
        VALUES (?, ?, 'quiz_completion', ?, ?)""", (user_id, xp_earned, f'Completed {difficulty} quiz', quiz_id))
        cursor.execute("""UPDATE user_stats SET total_tests = total_tests + 1, total_correct = total_correct + ?,
        total_questions = total_questions + ? WHERE user_id = ?""", (score, total, user_id))
    except Exception as e:
        print(f"Error saving score: {e}")
    
    # Update level progress if company mock
    if company_name:
        company_name_upper = company_name.upper()
        
        # Update best score
        cursor.execute("""SELECT best_score FROM company_level_progress 
            WHERE user_id = ? AND company_name = ? AND level = ?""",
            (user_id, company_name_upper, level))
        current_best = cursor.fetchone()
        
        if current_best and percentage > current_best['best_score']:
            cursor.execute("""UPDATE company_level_progress SET best_score = ? 
                WHERE user_id = ? AND company_name = ? AND level = ?""",
                (int(percentage), user_id, company_name_upper, level))
        
        # Unlock next level based on score
        if level == 1 and percentage >= 60:
            cursor.execute("""UPDATE company_level_progress SET unlocked = 1 
                WHERE user_id = ? AND company_name = ? AND level = 2""",
                (user_id, company_name_upper))
        elif level == 2 and percentage >= 70:
            cursor.execute("""UPDATE company_level_progress SET unlocked = 1 
                WHERE user_id = ? AND company_name = ? AND level = 3""",
                (user_id, company_name_upper))
    
    conn.commit()
    conn.close()
    
    adaptive_result = _update_category_performance(user_id, quiz_id, difficulty, score, total)
    
    return jsonify({
        'score': score,
        'total': total,
        'percentage': round(percentage, 2),
        'section_scores': section_breakdown,
        'readiness': round(readiness, 1),
        'readiness_status': readiness_status,
        'results': results,
        'xp_earned': xp_earned,
        'adaptive': adaptive_result
    })

@app.route("/results")
@login_required
def results():
    return render_template("results.html")

@app.route("/coding")
def coding():
    return render_template("coding.html")

@app.route("/code-practice")
@login_required
def code_practice():
    return render_template("code_practice_new.html")

@app.route("/problem/<int:problem_id>")
@login_required
def view_problem(problem_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (problem_id,))
    problem = cursor.fetchone()
    if not problem:
        conn.close()
        return "<h1>Problem Not Found</h1>", 404
    cursor.execute("SELECT * FROM problem_solutions WHERE problem_id = ?", (problem_id,))
    solutions = cursor.fetchall()
    conn.close()
    solutions_by_lang = {}
    for solution in solutions:
        solutions_by_lang[solution['language']] = {
            'code': solution['code'],
            'time_complexity': solution['time_complexity'],
            'space_complexity': solution['space_complexity'],
            'explanation': solution['explanation']
        }
    return render_template("problem.html", problem=problem, solutions=solutions_by_lang)

@app.route("/api/execute-code", methods=["POST"])
@login_required
def execute_code():
    import subprocess, tempfile, os, shutil
    data = request.get_json()
    code = data.get('code')
    language_id = data.get('language_id')
    stdin = data.get('stdin', '')
    if not code or not language_id:
        return jsonify({'error': 'Code and language_id are required'}), 400
    try:
        language_id = str(language_id)
        lang_config = {
            '71': {'name': 'Python', 'ext': '.py', 'compile': None, 'run': lambda f: ['python', f]},
            '50': {'name': 'C', 'ext': '.c', 'compile': lambda f: ['gcc', f, '-o', f.replace('.c', '')], 'run': lambda f: [f.replace('.c', '')]},
            '54': {'name': 'C++', 'ext': '.cpp', 'compile': lambda f: ['g++', f, '-o', f.replace('.cpp', '')], 'run': lambda f: [f.replace('.cpp', '')]},
            '62': {'name': 'Java', 'ext': '.java', 'compile': lambda f: ['javac', f], 'run': lambda f: ['java', '-cp', os.path.dirname(f), os.path.basename(f).replace('.java', '')]},
            '73': {'name': 'JavaScript', 'ext': '.js', 'compile': None, 'run': lambda f: ['node', f]},
        }
        if language_id not in lang_config:
            return jsonify({'error': 'Unsupported language'}), 400
        config = lang_config[language_id]
        temp_dir = tempfile.mkdtemp()
        try:
            filename = f"program{config['ext']}"
            temp_file = os.path.join(temp_dir, filename)
            with open(temp_file, 'w') as f:
                f.write(code)
            compile_output, stderr, stdout = '', '', ''
            if config['compile']:
                try:
                    compile_cmd = config['compile'](temp_file)
                    result = subprocess.run(compile_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        return jsonify({'stdout': '', 'stderr': result.stderr if result.stderr else 'Compilation failed', 'status': 'Compilation error'})
                    if result.stderr:
                        compile_output = result.stderr
                except FileNotFoundError as e:
                    return jsonify({'error': f'Compiler not found: {config["name"]}'}), 500
            try:
                run_cmd = config['run'](temp_file)
                result = subprocess.run(run_cmd, input=stdin, capture_output=True, text=True, timeout=10, cwd=temp_dir)
                stdout, stderr = result.stdout if result.stdout else '', result.stderr if result.stderr else ''
                return jsonify({'stdout': stdout if stdout else '(Program executed with no output)', 'stderr': stderr, 'status': 'Executed successfully' if result.returncode == 0 else f'Runtime error', 'compile_output': compile_output})
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Execution timed out'}), 408
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/aptitude")
@login_required
def aptitude():
    return render_template("aptitude.html")

@app.route("/technical")
@login_required
def technical():
    return render_template("technical.html")

@app.route("/mock")
@login_required
def mock():
    return render_template("mock.html")

@app.route("/leaderboard")
@login_required
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.id, u.username, u.age, u.gender, COUNT(DISTINCT us.quiz_id) as quizzes_completed,
        ROUND(AVG(us.percentage), 2) as avg_percentage, SUM(us.score) as total_score
        FROM users u LEFT JOIN user_scores us ON u.id = us.user_id GROUP BY u.id ORDER BY avg_percentage DESC, total_score DESC""")
    users = cursor.fetchall()
    current_user_id = session.get('user_id')
    cursor.execute("""SELECT u.id, u.username, u.age, u.gender, u.mobile_number, COUNT(DISTINCT us.quiz_id) as quizzes_completed,
        ROUND(AVG(us.percentage), 2) as avg_percentage, SUM(us.score) as total_score
        FROM users u LEFT JOIN user_scores us ON u.id = us.user_id WHERE u.id = ? GROUP BY u.id""", (current_user_id,))
    current_user = cursor.fetchone()
    conn.close()
    current_rank = None
    for idx, user in enumerate(users, 1):
        if user['id'] == current_user_id:
            current_rank = idx
            break
    leaderboard_data = [{'rank': idx + 1, 'username': user['username'], 'age': user['age'], 'gender': user['gender'],
        'quizzes_completed': user['quizzes_completed'] or 0, 'avg_percentage': user['avg_percentage'] or 0,
        'total_score': user['total_score'] or 0, 'is_current': user['id'] == current_user_id}
        for idx, user in enumerate(users)]
    return render_template("leaderboard.html", leaderboard=leaderboard_data, current_user=current_user, current_rank=current_rank)

@app.route("/profile")
@login_required
def profile():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, username, mobile_number, gender, age, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return redirect(url_for('logout'))
    cursor.execute("""SELECT COUNT(DISTINCT quiz_id) as total_quizzes, COUNT(DISTINCT quiz_id || difficulty) as attempts,
        ROUND(AVG(percentage), 2) as avg_percentage, MAX(percentage) as best_score, SUM(score) as total_score, SUM(total) as total_questions
        FROM user_scores WHERE user_id = ?""", (user_id,))
    stats = cursor.fetchone()
    cursor.execute("""SELECT us.id, q.name as quiz_name, us.difficulty, us.score, us.total, us.percentage, us.completed_at
        FROM user_scores us JOIN quizzes q ON us.quiz_id = q.id WHERE us.user_id = ? ORDER BY us.completed_at DESC LIMIT 10""", (user_id,))
    recent_quizzes = cursor.fetchall()
    conn.close()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.id, ROUND(AVG(us.percentage), 2) as avg_percentage, SUM(us.score) as total_score
        FROM users u LEFT JOIN user_scores us ON u.id = us.user_id GROUP BY u.id ORDER BY avg_percentage DESC, total_score DESC""")
    rankings = cursor.fetchall()
    user_rank = None
    for idx, rank_user in enumerate(rankings, 1):
        if rank_user['id'] == user_id:
            user_rank = idx
            break
    conn.close()
    return render_template("profile.html", user=user, stats=stats, recent_quizzes=recent_quizzes, user_rank=user_rank)

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    user_stats = cursor.fetchone()
    cursor.execute("SELECT * FROM xp_points WHERE user_id = ?", (user_id,))
    xp_data = cursor.fetchone()
    cursor.execute("SELECT * FROM streak_tracking WHERE user_id = ?", (user_id,))
    streak_data = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as total FROM user_scores WHERE user_id = ?", (user_id,))
    total_tests = cursor.fetchone()['total']
    cursor.execute("SELECT ROUND(AVG(percentage), 2) as avg FROM user_scores WHERE user_id = ?", (user_id,))
    avg_accuracy = cursor.fetchone()['avg'] or 0
    cursor.execute("""SELECT q.name, ROUND(AVG(us.percentage), 2) as avg_score, COUNT(*) as attempts
        FROM user_scores us JOIN quizzes q ON us.quiz_id = q.id WHERE us.user_id = ? GROUP BY q.id ORDER BY avg_score DESC""", (user_id,))
    category_performance = [dict(row) for row in cursor.fetchall()]
    strongest = category_performance[0]['name'] if category_performance else None
    weakest = category_performance[-1]['name'] if len(category_performance) > 1 else strongest
    week_start = date.today() - timedelta(days=6)
    cursor.execute("""SELECT DATE(completed_at) as day, COUNT(*) as tests, ROUND(AVG(percentage), 2) as avg_pct
        FROM user_scores WHERE user_id = ? AND DATE(completed_at) >= ? GROUP BY DATE(completed_at) ORDER BY day""", (user_id, week_start))
    weekly_data = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM xp_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user_id,))
    xp_history = [dict(row) for row in cursor.fetchall()]
    cursor.execute("""SELECT b.*, ub.earned_at FROM user_badges ub JOIN badges b ON ub.badge_id = b.id WHERE ub.user_id = ? ORDER BY ub.earned_at DESC""", (user_id,))
    user_badges = [dict(row) for row in cursor.fetchall()]
    current_xp = xp_data['xp'] if xp_data else 0
    current_level = 'Beginner'
    next_level, next_level_xp, progress_percent = None, None, 0
    for level, threshold in sorted(BADGE_LEVELS.items(), key=lambda x: x[1]):
        if current_xp >= threshold:
            current_level = level
        elif next_level is None:
            next_level = level
            next_level_xp = threshold
            break
    if next_level_xp:
        prev_xp = BADGE_LEVELS.get(current_level, 0)
        progress_percent = ((current_xp - prev_xp) / (next_level_xp - prev_xp)) * 100
    conn.close()
    return render_template("dashboard.html", total_tests=total_tests, avg_accuracy=avg_accuracy,
        strongest_category=strongest, weakest_category=weakest, weekly_data=weekly_data,
        category_performance=category_performance, xp_data=xp_data, streak_data=streak_data,
        user_stats=user_stats, xp_history=xp_history, user_badges=user_badges,
        current_level=current_level, next_level=next_level, next_level_xp=next_level_xp,
        progress_percent=round(progress_percent, 1), badge_levels=BADGE_LEVELS)


def _calculate_recommended_difficulty(accuracy, current_difficulty):
    """Calculate recommended difficulty based on user performance."""
    difficulty_order = ['Easy', 'Medium', 'Hard']
    current_index = difficulty_order.index(current_difficulty) if current_difficulty in difficulty_order else 0
    
    if accuracy > 80:
        if current_index < len(difficulty_order) - 1:
            return difficulty_order[current_index + 1], 'increase'
        return current_difficulty, 'max'
    elif accuracy < 50:
        if current_index > 0:
            return difficulty_order[current_index - 1], 'decrease'
        return current_difficulty, 'min'
    else:
        return current_difficulty, 'maintain'


def _update_category_performance(user_id, quiz_id, difficulty, score, total):
    """Update user's performance in a category."""
    percentage = (score / total * 100) if total > 0 else 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM category_performance WHERE user_id = ? AND quiz_id = ?", (user_id, quiz_id))
    existing = cursor.fetchone()
    
    if existing:
        new_attempts = existing['attempts'] + 1
        new_correct = existing['correct_answers'] + score
        new_total = existing['total_questions'] + total
        new_accuracy = (new_correct / new_total * 100) if new_total > 0 else 0
        recommended, change_type = _calculate_recommended_difficulty(new_accuracy, difficulty)
        
        cursor.execute("""UPDATE category_performance SET attempts = ?, correct_answers = ?, 
            total_questions = ?, average_accuracy = ?, last_attempt = ?, recommended_difficulty = ?
            WHERE user_id = ? AND quiz_id = ?""", 
            (new_attempts, new_correct, new_total, new_accuracy, date.today(), recommended, user_id, quiz_id))
    else:
        recommended, change_type = _calculate_recommended_difficulty(percentage, difficulty)
        cursor.execute("""INSERT INTO category_performance 
            (user_id, quiz_id, attempts, correct_answers, total_questions, average_accuracy, last_attempt, recommended_difficulty)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?)""", (user_id, quiz_id, score, total, percentage, date.today(), recommended))
    
    conn.commit()
    conn.close()
    
    return {'accuracy': percentage, 'recommended_difficulty': recommended, 'change_type': change_type}


@app.route("/api/adaptive-difficulty/<int:quiz_id>")
@login_required
def get_adaptive_difficulty(quiz_id):
    """Get recommended difficulty for a user based on their performance in a category."""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM category_performance WHERE user_id = ? AND quiz_id = ?", (user_id, quiz_id))
    performance = cursor.fetchone()
    
    cursor.execute("SELECT DISTINCT difficulty FROM questions WHERE quiz_id = ? ORDER BY difficulty", (quiz_id,))
    available_levels = [row['difficulty'] for row in cursor.fetchall()]
    
    conn.close()
    
    if performance:
        return jsonify({
            'has_history': True,
            'recommended_difficulty': performance['recommended_difficulty'],
            'current_accuracy': round(performance['average_accuracy'], 2),
            'total_attempts': performance['attempts'],
            'available_levels': available_levels
        })
    else:
        return jsonify({
            'has_history': False,
            'recommended_difficulty': 'Easy',
            'current_accuracy': 0,
            'total_attempts': 0,
            'available_levels': available_levels
        })


@app.route("/api/category-stats")
@login_required
def get_category_stats():
    """Get overall category performance statistics."""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""SELECT q.name as category_name, cp.attempts, cp.correct_answers, cp.total_questions,
        cp.average_accuracy, cp.recommended_difficulty, cp.last_attempt
        FROM category_performance cp JOIN quizzes q ON cp.quiz_id = q.id WHERE cp.user_id = ?
        ORDER BY cp.average_accuracy DESC""", (user_id,))
    
    categories = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'categories': [{'name': c['category_name'], 'attempts': c['attempts'], 'correct': c['correct_answers'],
            'total': c['total_questions'], 'accuracy': round(c['average_accuracy'], 2) if c['average_accuracy'] else 0,
            'recommended': c['recommended_difficulty'], 'last_attempt': c['last_attempt']} for c in categories]
    })


@app.route("/api/evaluate-code", methods=["POST"])
@login_required
def evaluate_code():
    """Evaluate Python code for company mock coding questions."""
    import subprocess
    
    data = request.get_json()
    code = data.get('code', '')
    expected_output = data.get('expected_output', '').strip()
    
    # Security check
    forbidden = ['import os', 'import sys', 'open(', 'exec(', 'eval(', '__import__']
    code_lower = code.lower()
    for f in forbidden:
        if f in code_lower:
            return jsonify({'correct': False, 'output': 'Security: Forbidden keyword detected', 'error': True})
    
    # Run code with timeout
    try:
        result = subprocess.run(
            ['python', '-c', code],
            capture_output=True,
            text=True,
            timeout=3
        )
        output = result.stdout.strip()
        
        if output == expected_output:
            return jsonify({'correct': True, 'output': output})
        else:
            return jsonify({'correct': False, 'output': output, 'expected': expected_output})
    except subprocess.TimeoutExpired:
        return jsonify({'correct': False, 'output': 'Timeout: Code took too long', 'error': True})
    except Exception as e:
        return jsonify({'correct': False, 'output': str(e), 'error': True})


if __name__ == "__main__":
    import os
    if not os.path.exists(DB_PATH):
        from database import init_db
        init_db()
    app.run(debug=True)
