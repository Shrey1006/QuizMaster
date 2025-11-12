from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)
 
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    fullName = db.Column(db.String)
    role = db.Column(db.String)

class Quiz(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    category = db.Column(db.String)
    difficulty = db.Column(db.String)
    duration = db.Column(db.Integer)
    passingScore = db.Column(db.Integer)

class Question(db.Model):
    id = db.Column(db.String, primary_key=True)
    quiz_id = db.Column(db.String, db.ForeignKey('quiz.id'))
    text = db.Column(db.String)
    options = db.Column(db.String)   # Stored as JSON string
    correctAnswer = db.Column(db.Integer)
    explanation = db.Column(db.String)

class ResultHistory(db.Model):
    id = db.Column(db.String, primary_key=True)
    userId = db.Column(db.String)
    quizTitle = db.Column(db.String)
    date = db.Column(db.String)
    score = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    timeTaken = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    total = db.Column(db.Integer)
    difficulty = db.Column(db.String)

class Feedback(db.Model):
    id = db.Column(db.String, primary_key=True)
    userId = db.Column(db.String)
    quizId = db.Column(db.String)
    comments = db.Column(db.String)
    rating = db.Column(db.Integer)
    date = db.Column(db.String)

# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('usernameOrEmail')
    user = User.query.filter_by(username=username).first()
    if user:
        token = str(uuid.uuid4())  # Mock token
        return jsonify({"message": "Login successful", "user": {
            "id": user.id, "username": user.username, "fullName": user.fullName, "role": user.role}, "token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 400
    new_user = User(id=str(uuid.uuid4()), username=username, fullName=data.get('fullName'), role='user')
    db.session.add(new_user)
    db.session.commit()
    token = str(uuid.uuid4())
    return jsonify({"message": "Registration successful", "user": {"id": new_user.id, "username": new_user.username, "fullName": new_user.fullName, "role": new_user.role}, "token": token}), 201

# Quiz endpoints
@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    quizzes_out = []
    for q in quizzes:
        questions = Question.query.filter_by(quiz_id=q.id).all()
        questions_out = []
        for question in questions:
            questions_out.append({
                "id": question.id,
                "text": question.text,
                "options": json.loads(question.options),
                "correctAnswer": question.correctAnswer,
                "explanation": question.explanation
            })
        quizzes_out.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "category": q.category,
            "difficulty": q.difficulty,
            "duration": q.duration,
            "passingScore": q.passingScore,
            "questions": questions_out
        })
    return jsonify(quizzes_out), 200

@app.route('/api/quizzes', methods=['POST'])
def create_quiz():
    data = request.json
    if not all(k in data for k in ['title', 'description', 'questions']):
        return jsonify({"message": "Missing required quiz fields"}), 400

    for question in data['questions']:
        if not all(k in question for k in ['text', 'options', 'correctAnswer']):
            return jsonify({"message": "All questions must have text, options, and a correct answer."}), 400

    quiz_id = str(uuid.uuid4())
    quiz = Quiz(
        id=quiz_id,
        title=data['title'],
        description=data['description'],
        category=data.get('category', 'General'),
        difficulty=data.get('difficulty', 'Medium'),
        duration=data.get('duration', 15),
        passingScore=data.get('passingScore', 70)
    )
    db.session.add(quiz)
    db.session.commit()
    for q in data['questions']:
        question = Question(id=str(uuid.uuid4()), quiz_id=quiz_id, text=q['text'],
                            options=json.dumps(q['options']), correctAnswer=q['correctAnswer'],
                            explanation=q.get('explanation', ''))
        db.session.add(question)
    db.session.commit()

    return jsonify({"message": "Quiz created successfully", "quiz": {
        "id": quiz.id, "title": quiz.title, "description": quiz.description, "category": quiz.category,
        "difficulty": quiz.difficulty, "duration": quiz.duration, "passingScore": quiz.passingScore}}), 201

# Results endpoints
@app.route('/api/results', methods=['POST'])
def save_result():
    data = request.json
    result_entry = ResultHistory(
        id=str(uuid.uuid4()),
        userId=data.get('userId'),
        quizTitle=data.get('quizTitle'),
        date=datetime.now().strftime("%Y-%m-%d"),
        score=data.get('score'),
        passed=data.get('passed'),
        timeTaken=data.get('timeTaken'),
        correct=data.get('correct'),
        total=data.get('total'),
        difficulty=data.get('difficulty'),
    )
    db.session.add(result_entry)
    db.session.commit()
    return jsonify({"message": "Result saved successfully"}), 201

@app.route('/api/results/<user_id>', methods=['GET'])
def get_results(user_id):
    results = ResultHistory.query.filter_by(userId=user_id).all()
    results_out = []
    for r in results:
        results_out.append({
            "id": r.id,
            "userId": r.userId,
            "quizTitle": r.quizTitle,
            "date": r.date,
            "score": r.score,
            "passed": r.passed,
            "timeTaken": r.timeTaken,
            "correct": r.correct,
            "total": r.total,
            "difficulty": r.difficulty,
        })
    return jsonify(results_out), 200

# Feedback endpoint(s)
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    feedback = Feedback(
        id=str(uuid.uuid4()),
        userId=data.get('userId'),
        quizId=data.get('quizId'),
        comments=data.get('comments', ''),
        rating=data.get('rating'),
        date=datetime.now().strftime("%Y-%m-%d")
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback submitted successfully"}), 201

@app.route('/api/feedback', methods=['GET'])
def list_feedback():
    feedback_list = Feedback.query.order_by(Feedback.date.desc()).all()
    out = []
    for f in feedback_list:
        out.append({
            "id": f.id,
            "userId": f.userId,
            "quizId": f.quizId,
            "comments": f.comments,
            "rating": f.rating,
            "date": f.date
        })
    return jsonify(out), 200

# Delete quiz (and its questions)
@app.route('/api/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404
    # Delete questions first due to FK
    Question.query.filter_by(quiz_id=quiz_id).delete()
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz deleted"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)