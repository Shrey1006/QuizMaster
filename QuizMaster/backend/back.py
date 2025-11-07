from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# -------------------------------
# Mock database structures
# -------------------------------

QUIZZES = [
    # Sample quiz data structure
    {
        "id": "js-fund",
        "title": "JavaScript Fundamentals",
        "description": "Test your basic knowledge of JS, variables, and loops.",
        "category": "Programming",
        "difficulty": "Easy",
        "duration": 15,
        "passingScore": 70,
        "questions": [
            {
                "id": "q1",
                "text": "What is 'this' in JavaScript?",
                "options": ["The current object", "A variable name", "A function call", "The global scope"],
                "correctAnswer": 0,
                "explanation": "'this' refers to the object it belongs to."
            }
        ],
        "rating": 4.5,
        "participants": 1200,
        "createdDate": "2025-05-10",
        "status": "active"
    },
    {
        "id": "react-hooks",
        "title": "React Hooks Mastery",
        "description": "Advanced concepts on useState, useEffect, and custom hooks.",
        "category": "Programming",
        "difficulty": "Hard",
        "duration": 25,
        "passingScore": 80,
        "questions": [
            {
                "id": "q2",
                "text": "Which hook manages side effects?",
                "options": ["useState", "useContext", "useEffect", "useReducer"],
                "correctAnswer": 2,
                "explanation": "useEffect is used for side effects."
            }
        ],
        "rating": 4.8,
        "participants": 800,
        "createdDate": "2025-06-01",
        "status": "active"
    }
]

USERS = {
    # username: user info dict
    "johndoe": {"id": "u1", "username": "johndoe", "fullName": "John Doe", "role": "user", "password": "pass123"},
    "admin": {"id": "a1", "username": "admin", "fullName": "Admin User", "role": "admin", "password": "adminpass"}
}

RESULTSHISTORY = [
    {
        "id": "res1",
        "userId": "u1",
        "quizTitle": "JavaScript Fundamentals",
        "date": "2025-10-14",
        "score": 85,
        "passed": True,
        "timeTaken": 420,
        "correct": 17,
        "total": 20,
        "difficulty": "Medium"
    },
    {
        "id": "res2",
        "userId": "u1",
        "quizTitle": "React Hooks Mastery",
        "date": "2025-10-13",
        "score": 92,
        "passed": True,
        "timeTaken": 540,
        "correct": 23,
        "total": 25,
        "difficulty": "Hard"
    }
]

# -------------------------------
# Authentication endpoints
# -------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("usernameOrEmail")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "Missing credentials."}), 400

    # Mock lookup by username only
    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"message": "Invalid credentials."}), 401
    
    # In real app, generate JWT or session token
    token = str(uuid.uuid4())
    return jsonify({"message": "Login successful", "user": user, "token": token}), 200


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    if not username or username in USERS:
        return jsonify({"message": "Username already taken or invalid."}), 400

    password = data.get("password")
    fullName = data.get("fullName", "")
    if not password:
        return jsonify({"message": "Password is required."}), 400

    # Generate user ID and save user
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "username": username,
        "fullName": fullName,
        "role": "user",
        "password": password  # store hashed password in real app
    }
    USERS[username] = new_user

    token = str(uuid.uuid4())
    return jsonify({"message": "Registration successful", "user": new_user, "token": token}), 201

# -------------------------------
# Quiz endpoints
# -------------------------------

@app.route("/api/quizzes", methods=["GET"])
def get_quizzes():
    return jsonify(QUIZZES), 200

@app.route("/api/quizzes", methods=["POST"])
def create_quiz():
    data = request.json
    required_fields = ["title", "description", "questions"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required quiz fields."}), 400

    if not isinstance(data["questions"], list) or len(data["questions"]) == 0:
        return jsonify({"message": "Quiz must have at least one question."}), 400
    
    for q in data["questions"]:
        if not all(k in q for k in ("text", "options", "correctAnswer")):
            return jsonify({"message": "Each question must have text, options and correct answer."}), 400
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            return jsonify({"message": "Each question options must be a list with at least two items."}), 400
        if not (0 <= q["correctAnswer"] < len(q["options"])):
            return jsonify({"message": "Correct answer index is out of bounds."}), 400

    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": data["title"],
        "description": data.get("description", ""),
        "category": data.get("category", "General"),
        "difficulty": data.get("difficulty", "Medium"),
        "duration": data.get("duration", 15),
        "passingScore": data.get("passingScore", 70),
        "questions": data["questions"],
        "rating": 0,
        "participants": 0,
        "createdDate": datetime.now().strftime("%Y-%m-%d"),
        "status": "active"
    }
    QUIZZES.append(new_quiz)

    return jsonify({"message": "Quiz created successfully", "quiz": new_quiz}), 201

# -------------------------------
# Results endpoints
# -------------------------------

@app.route("/api/results", methods=["POST"])
def save_result():
    data = request.json
    required_fields = ["userId", "quizTitle", "score", "passed", "timeTaken", "correct", "total", "difficulty"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required result fields."}), 400

    result_entry = {
        "id": str(uuid.uuid4()),
        "userId": data["userId"],
        "quizTitle": data["quizTitle"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": data["score"],
        "passed": data["passed"],
        "timeTaken": data["timeTaken"],
        "correct": data["correct"],
        "total": data["total"],
        "difficulty": data["difficulty"]
    }
    RESULTSHISTORY.append(result_entry)

    return jsonify({"message": "Result saved successfully"}), 201

@app.route("/api/results/<userId>", methods=["GET"])
def get_results(userId):
    user_results = [r for r in RESULTSHISTORY if r["userId"] == userId]
    return jsonify(user_results), 200

# -------------------------------
# Main app entry
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5001)
