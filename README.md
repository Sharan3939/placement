# 🎓 Placement Preparation Portal

A comprehensive web-based platform for interview preparation covering **Aptitude**, **Coding**, and **Technical** topics.

## Features

✅ **Interactive Quizzes** - Multiple choice questions with instant feedback  
✅ **Score Tracking** - Get detailed results with explanations  
✅ **Full-Length Mock Tests** - Assess your overall readiness  
✅ **Database-Driven** - SQLite database with expandable question bank  
✅ **Responsive Design** - Beautiful UI with gradient backgrounds  
✅ **Instant Feedback** - Understand your mistakes with explanations  

## Project Structure

```
placement/
├── app.py                 # Flask application with all routes
├── database.py            # Database initialization and schema
├── requirements.txt       # Python dependencies
├── placement.db          # SQLite database (auto-created)
├── static/
│   └── style.css         # Complete styling for the site
└── templates/
    ├── index.html        # Home page with category cards
    ├── quiz.html         # Quiz interface
    ├── results.html      # Results and detailed feedback
    ├── aptitude.html     # Aptitude section page
    ├── coding.html       # Coding section page
    ├── technical.html    # Technical section page
    └── mock.html         # Mock test information page
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python database.py
```
This will create `placement.db` with:
- 4 quizzes (Aptitude, Coding, Technical, Mock Test)
- 15 sample questions with explanations
- Proper database schema

### Step 3: Run the Application
```bash
python app.py
```
OR
```bash
python -m flask run
```

The application will start on `http://localhost:5000`

## Usage

### Home Page
- Access all quiz categories from the home page
- View quiz statistics (number of questions, time duration)
- Start any quiz by clicking the category button

### Taking a Quiz
1. Select a category from home page
2. Read each question carefully
3. Select your answer from 4 options
4. Progress bar shows completion status
5. Click "Submit Quiz" when all questions are answered

### Viewing Results
- Instant score calculation
- Performance message based on percentage
- Detailed review of each question
- Correct answer with explanation
- Your answer highlighted for comparison

## Quiz Categories

### 📊 Aptitude (5 Questions, 15 minutes)
- Percentages & Ratios
- Speed & Distance
- Averages & Statistics
- Profit & Loss
- Reasoning

### 💻 Coding (5 Questions, 20 minutes)
- Python Basics
- Data Structures
- Control Statements
- Functions
- Algorithms

### 🔧 Technical (5 Questions, 15 minutes)
- Database Normalization
- SQL & Queries
- Operating Systems
- Networks
- ACID Properties

### 🎯 Mock Test (15 Questions, 50 minutes)
- Full-length comprehensive test
- Mix of all topics
- Realistic exam simulation

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/quiz/<category>` | GET | Display quiz for category |
| `/api/submit-quiz` | POST | Submit quiz answers and get results |
| `/results` | GET | Show quiz results |
| `/aptitude` | GET | Aptitude section info page |
| `/coding` | GET | Coding section info page |
| `/technical` | GET | Technical section info page |
| `/mock` | GET | Mock test info page |

## Database Schema

### Quizzes Table
```sql
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    category TEXT,
    description TEXT
)
```

### Questions Table
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    quiz_id INTEGER,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_answer TEXT,
    explanation TEXT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
)
```

## Customization

### Adding More Questions
Edit `database.py` and add questions to the respective tuples:
- `aptitude_qs` - Aptitude questions
- `coding_qs` - Coding questions
- `technical_qs` - Technical questions

Then re-run:
```bash
python database.py
```

### Changing Quiz Time Duration
Update the display in the respective `.html` files or modify in `database.py` quiz descriptions.

### Styling
All CSS is in `static/style.css`. The design uses:
- Modern purple gradient (#667eea to #764ba2)
- Responsive grid layout
- Smooth transitions and hover effects

## Performance Tips

1. **Time Yourself** - Use the mock test to practice time management
2. **Review Explanations** - Understand why your answer was wrong
3. **Practice Multiple Times** - Take quizzes multiple times to improve
4. **Track Progress** - Keep notes of your weak areas

## Troubleshooting

### Database Error
If you get a database error, try:
```bash
rm placement.db
python database.py
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### CSS Not Loading
Ensure Flask is serving static files correctly. Check if `static/style.css` exists.

## Future Enhancements

- 🔐 User authentication and login
- 📈 Progress tracking and leaderboards
- 🌙 Dark mode
- 📱 Mobile app version
- 🎥 Video explanations
- 💬 Discussion forum
- 🔔 Push notifications
- 📊 Analytics dashboard

## License

This project is open source and available for educational purposes.

## Support

For issues or suggestions, please create an issue in the project repository.

---

**Happy Learning! All the best for your placements! 🚀**
