from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from werkzeug.utils import secure_filename
import PyPDF2
import io
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://adwait:adwait@cluster0.teugbgb.mongodb.net/?appName=Cluster0')
DB_NAME = 'resume_analyzer'
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db.users
    scores_collection = db.assessment_scores
    # Test connection
    client.admin.command('ping')
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"⚠ MongoDB connection error: {e}")
    print("⚠ Continuing without MongoDB - some features may not work")

# Initialize Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Skill Assessment Questions
ASSESSMENTS = {
    'sql': {
        'title': 'SQL Assessment',
        'questions': [
            {
                'id': 1,
                'question': 'What does SQL stand for?',
                'options': [
                    'Structured Query Language',
                    'Simple Query Language',
                    'Standard Query Language',
                    'Sequential Query Language'
                ],
                'correct': 0
            },
            {
                'id': 2,
                'question': 'Which SQL statement is used to extract data from a database?',
                'options': ['EXTRACT', 'SELECT', 'GET', 'OPEN'],
                'correct': 1
            },
            {
                'id': 3,
                'question': 'Which SQL statement is used to update data in a database?',
                'options': ['MODIFY', 'UPDATE', 'SAVE', 'CHANGE'],
                'correct': 1
            },
            {
                'id': 4,
                'question': 'Which SQL statement is used to delete data from a database?',
                'options': ['REMOVE', 'DELETE', 'COLLAPSE', 'TRUNCATE'],
                'correct': 1
            },
            {
                'id': 5,
                'question': 'What is the purpose of the WHERE clause in SQL?',
                'options': [
                    'To specify which columns to select',
                    'To filter records based on conditions',
                    'To sort the results',
                    'To group records'
                ],
                'correct': 1
            },
            {
                'id': 6,
                'question': 'Which keyword is used to sort the result-set in ascending order?',
                'options': ['SORT BY', 'ORDER BY ASC', 'ORDER BY', 'SORT ASC'],
                'correct': 2
            },
            {
                'id': 7,
                'question': 'What does JOIN do in SQL?',
                'options': [
                    'Combines rows from two or more tables',
                    'Deletes duplicate rows',
                    'Sorts the table',
                    'Filters the table'
                ],
                'correct': 0
            },
            {
                'id': 8,
                'question': 'Which SQL function is used to count the number of rows?',
                'options': ['COUNT()', 'SUM()', 'TOTAL()', 'NUMBER()'],
                'correct': 0
            },
            {
                'id': 9,
                'question': 'What is the difference between INNER JOIN and LEFT JOIN?',
                'options': [
                    'INNER JOIN returns all rows from both tables, LEFT JOIN returns only matching rows',
                    'INNER JOIN returns only matching rows, LEFT JOIN returns all rows from left table',
                    'There is no difference',
                    'INNER JOIN is faster than LEFT JOIN'
                ],
                'correct': 1
            },
            {
                'id': 10,
                'question': 'Which SQL statement is used to create a new table?',
                'options': ['CREATE TABLE', 'NEW TABLE', 'ADD TABLE', 'MAKE TABLE'],
                'correct': 0
            }
        ]
    },
    'data_structures': {
        'title': 'Data Structures Assessment',
        'questions': [
            {
                'id': 1,
                'question': 'What is the time complexity of accessing an element in an array by index?',
                'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n²)'],
                'correct': 0
            },
            {
                'id': 2,
                'question': 'Which data structure follows LIFO (Last In First Out) principle?',
                'options': ['Queue', 'Stack', 'Array', 'Linked List'],
                'correct': 1
            },
            {
                'id': 3,
                'question': 'What is the time complexity of inserting an element at the beginning of a linked list?',
                'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n²)'],
                'correct': 0
            },
            {
                'id': 4,
                'question': 'Which data structure is best for implementing a priority queue?',
                'options': ['Array', 'Linked List', 'Heap', 'Stack'],
                'correct': 2
            },
            {
                'id': 5,
                'question': 'What is the time complexity of binary search on a sorted array?',
                'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n²)'],
                'correct': 2
            },
            {
                'id': 6,
                'question': 'Which traversal method visits root, left subtree, then right subtree?',
                'options': ['Inorder', 'Preorder', 'Postorder', 'Level order'],
                'correct': 1
            },
            {
                'id': 7,
                'question': 'What is the worst-case time complexity of quicksort?',
                'options': ['O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'],
                'correct': 2
            },
            {
                'id': 8,
                'question': 'Which data structure uses hash function for storing data?',
                'options': ['Array', 'Hash Table', 'Stack', 'Queue'],
                'correct': 1
            },
            {
                'id': 9,
                'question': 'What is the space complexity of merge sort?',
                'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n log n)'],
                'correct': 1
            },
            {
                'id': 10,
                'question': 'Which data structure is used for implementing breadth-first search?',
                'options': ['Stack', 'Queue', 'Heap', 'Array'],
                'correct': 1
            }
        ]
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def analyze_resume_with_gemini(resume_text):
    if not GEMINI_API_KEY:
        return {'error': 'Gemini API key not configured'}

    model_names = [
        "models/gemini-2.5-flash",   # fast + cheap
        "models/gemini-2.5-pro",     # best quality
        "models/gemini-2.0-flash"    # stable fallback
    ]

    prompt = f"""
Analyze the following resume and return STRICT JSON only.

Resume:
{resume_text}

JSON format:
{{
  "overall_assessment": "",
  "strengths": [],
  "improvements": [],
  "missing_skills": [],
  "recommended_courses": [
    {{
      "name": "",
      "description": "",
      "reason": ""
    }}
  ],
  "career_suggestions": []
}}
"""

    last_error = None

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()

            # strip markdown if model adds it
            if "```" in text:
                text = text.split("```")[1]

            return json.loads(text)

        except Exception as e:
            last_error = str(e)

    return {
        "error": "All Gemini models failed",
        "details": last_error
    }


# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'created_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Set session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            }
        })
    except Exception as e:
        return jsonify({'error': f'Signup failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = str(user['_id'])
        session['user_email'] = user['email']
        session['user_name'] = user.get('name', '')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', '')
            }
        })
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'email': session.get('user_email'),
                'name': session.get('user_name')
            }
        })
    return jsonify({'authenticated': False}), 401

# Main Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user/scores', methods=['GET'])
@login_required
def get_user_scores():
    """Get user's latest assessment scores"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get latest score for each assessment
        scores = list(scores_collection.find(
            {'user_id': user_id}
        ).sort('timestamp', -1))
        
        # Group by assessment and get latest
        latest_scores = {}
        for score in scores:
            assessment_id = score.get('assessment_id')
            if assessment_id not in latest_scores:
                latest_scores[assessment_id] = score
        
        # Format response
        result = []
        for assessment_id, score in latest_scores.items():
            result.append({
                'assessment_id': assessment_id,
                'assessment_title': score.get('assessment_title', assessment_id),
                'score': score.get('score', 0),
                'correct_count': score.get('correct_count', 0),
                'total_questions': score.get('total_questions', 0),
                'timestamp': score.get('timestamp').isoformat() if score.get('timestamp') else None
            })
        
        return jsonify({'scores': result})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch scores: {str(e)}'}), 500

@app.route('/api/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from file
        file.seek(0)  # Reset file pointer
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file)
        elif filename.endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Unsupported file type. Please upload PDF or TXT'}), 400
        
        # Analyze with Gemini
        analysis = analyze_resume_with_gemini(resume_text)
        
        # Store in session
        session['resume_analysis'] = analysis
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/assessments')
@login_required
def get_assessments():
    """Get list of available assessments"""
    return jsonify({
        'assessments': [
            {'id': 'sql', 'title': 'SQL Assessment'},
            {'id': 'data_structures', 'title': 'Data Structures Assessment'}
        ]
    })

@app.route('/api/assessments/<assessment_id>')
@login_required
def get_assessment(assessment_id):
    """Get specific assessment questions"""
    if assessment_id in ASSESSMENTS:
        # Return questions without correct answers
        assessment = ASSESSMENTS[assessment_id].copy()
        questions = []
        for q in assessment['questions']:
            question_data = {
                'id': q['id'],
                'question': q['question'],
                'options': q['options']
            }
            questions.append(question_data)
        
        return jsonify({
            'title': assessment['title'],
            'questions': questions
        })
    
    return jsonify({'error': 'Assessment not found'}), 404

@app.route('/api/assessments/<assessment_id>/submit', methods=['POST'])
@login_required
def submit_assessment(assessment_id):
    """Submit assessment answers and get results"""
    if assessment_id not in ASSESSMENTS:
        return jsonify({'error': 'Assessment not found'}), 404
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    answers = request.json.get('answers', {})
    assessment = ASSESSMENTS[assessment_id]
    
    correct_count = 0
    total_questions = len(assessment['questions'])
    results = []
    
    for question in assessment['questions']:
        q_id = question['id']
        user_answer = answers.get(str(q_id))
        correct_answer = question['correct']
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_count += 1
        
        results.append({
            'question_id': q_id,
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'correct_option': question['options'][correct_answer]
        })
    
    score = (correct_count / total_questions) * 100
    
    # Save score to MongoDB
    try:
        score_doc = {
            'user_id': user_id,
            'assessment_id': assessment_id,
            'assessment_title': assessment['title'],
            'score': round(score, 2),
            'correct_count': correct_count,
            'total_questions': total_questions,
            'timestamp': datetime.utcnow(),
            'results': results
        }
        scores_collection.insert_one(score_doc)
    except Exception as e:
        print(f"Warning: Failed to save score to MongoDB: {e}")
    
    return jsonify({
        'score': round(score, 2),
        'correct_count': correct_count,
        'total_questions': total_questions,
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
