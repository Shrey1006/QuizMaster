from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

# --- Mock Data Store (Replace with a real database in production) ---

# Stores quiz data created by the admin
QUIZZES = [
    {"id": "js-fund", "title": "JavaScript Fundamentals", "description": "Test your basic knowledge of JS, variables, and loops.", "category": "Programming", "difficulty": "Easy", "duration": 15, "passingScore": 70, "questions": [{"id": "q1", "text": "What is 'this' in JavaScript?", "options": ["The current object", "A variable name", "A function call", "The global scope"], "correctAnswer": 0, "explanation": "'this' refers to the object it belongs to."}], "rating": 4.5, "participants": 1200, "createdDate": "2025-05-10", "status": "active" },
    {"id": "react-hooks", "title": "React Hooks Mastery", "description": "Advanced concepts on useState, useEffect, and custom hooks.", "category": "Programming", "difficulty": "Hard", "duration": 25, "passingScore": 80, "questions": [{"id": "q2", "text": "Which hook manages side effects?", "options": ["useState", "useContext", "useEffect", "useReducer"], "correctAnswer": 2, "explanation": "useEffect is used for side effects."}], "rating": 4.8, "participants": 800, "createdDate": "2025-06-01", "status": "active" },
]

# Stores user data (for mock authentication)
USERS = {
    "johndoe": {"id": "u1", "username": "johndoe", "fullName": "John Doe", "role": "user"},
    "admin": {"id": "a1", "username": "admin", "fullName": "Admin User", "role": "admin"},
}

# Stores quiz results history
RESULTS_HISTORY = []

# --- AUTHENTICATION ENDPOINTS ---

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticates a user based on username (password check is mocked)."""
    data = request.json
    username = data.get('usernameOrEmail')

    # Mocked authentication: check if user exists in the store
    user = USERS.get(username)
    if user:
        # Generate a simple token (mocked JWT)
        token = str(uuid.uuid4())
        return jsonify({"message": "Login successful", "user": user, "token": token}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Registers a new user (mocked)."""
    data = request.json
    username = data.get('username')
    
    if username in USERS:
        return jsonify({"message": "Username already taken"}), 400

    new_user_id = str(uuid.uuid4())
    new_user = {
        "id": new_user_id,
        "username": username,
        "fullName": data.get('fullName'),
        "role": "user"
    }
    USERS[username] = new_user
    
    token = str(uuid.uuid4())
    return jsonify({"message": "Registration successful", "user": new_user, "token": token}), 201

# --- QUIZ MANAGEMENT ENDPOINTS ---

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    """Returns the list of available quizzes."""
    return jsonify(QUIZZES), 200

@app.route('/api/quizzes', methods=['POST'])
def create_quiz():
    """Allows admin to create a new quiz."""
    # NOTE: Authorization check (e.g., token validation and role check) is omitted for simplicity.
    data = request.json
    
    # Basic validation for quiz metadata
    if not all(k in data for k in ['title', 'description', 'questions']):
        return jsonify({"message": "Missing required quiz fields (title, description, questions)"}), 400

    # Detailed validation for questions
    if not isinstance(data['questions'], list) or not data['questions']:
        return jsonify({"message": "Quiz must contain at least one question"}), 400

    for question in data['questions']:
        if not all(k in question for k in ['text', 'options', 'correctAnswer']):
            return jsonify({"message": "All questions must have text, options, and a correct answer."}), 400
        if not isinstance(question['options'], list) or len(question['options']) < 2:
            return jsonify({"message": "Question options must be a list with at least two elements."}), 400
        if not (0 <= question['correctAnswer'] < len(question['options'])):
            return jsonify({"message": "Correct answer index is out of bounds for options."}), 400

    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": data['title'],
        "description": data['description'],
        "category": data.get('category', 'General'),
        "difficulty": data.get('difficulty', 'Medium'),
        "duration": data.get('duration', 15),
        "passingScore": data.get('passingScore', 70),
        "questions": data['questions'],
        "rating": 0,
        "participants": 0,
        "createdDate": datetime.now().strftime("%Y-%m-%d"),
        "status": "active"
    }

    QUIZZES.append(new_quiz)
    return jsonify({"message": "Quiz created successfully", "quiz": new_quiz}), 201

# --- RESULTS ENDPOINTS ---

@app.route('/api/results', methods=['POST'])
def save_result():
    """Saves a quiz result to the history."""
    data = request.json
    
    # In a real app, we'd verify the quiz ID and user ID
    result_entry = {
        "id": str(uuid.uuid4()),
        "userId": data.get('userId'),
        "quizTitle": data.get('quizTitle'),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": data.get('score'),
        "passed": data.get('passed'),
        "timeTaken": data.get('timeTaken'),
        "correct": data.get('correct'),
        "total": data.get('total'),
        "difficulty": data.get('difficulty')
    }
    
    RESULTS_HISTORY.append(result_entry)
    return jsonify({"message": "Result saved successfully"}), 201

@app.route('/api/results/<user_id>', methods=['GET'])
def get_results(user_id):
    """Returns the quiz history for a specific user."""
    # Since we don't track user IDs in mock data, we return all history for the demo
    return jsonify(RESULTS_HISTORY), 200


if __name__ == '__main__':
    # Add a couple of initial results for the history page to work immediately
    RESULTS_HISTORY.extend([
        {"id": "res1", "userId": "u1", "quizTitle": "JavaScript Fundamentals", "date": "2025-10-14", "score": 85, "passed": True, "timeTaken": 420, "correct": 17, "total": 20, "difficulty": "Medium"},
        {"id": "res2", "userId": "u1", "quizTitle": "React Hooks Mastery", "date": "2025-10-13", "score": 92, "passed": True, "timeTaken": 540, "correct": 23, "total": 25, "difficulty": "Hard"},
    ])
    
    # Force the server to run on port 5001 to avoid conflicts with port 3000
    app.run(debug=True, port=5001)