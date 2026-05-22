import os
import json
from datetime import datetime

def save_session_data(username, session_data):
    """Save exercise session data to JSON file"""
    os.makedirs('data/sessions', exist_ok=True)
    filename = f'data/sessions/{username}_sessions.json'
    
    sessions = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            sessions = json.load(f)
    
    sessions.append({
        'timestamp': datetime.now().isoformat(),
        'data': session_data
    })
    
    with open(filename, 'w') as f:
        json.dump(sessions, f, indent=2)
    
    return True

def get_user_history(username):
    """Get user exercise history"""
    filename = f'data/sessions/{username}_sessions.json'
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def calculate_performance_score(angles, exercise_type):
    """Calculate performance score based on joint angles"""
    if not angles:
        return 0
    
    total_score = 0
    target_angles = {
        'shoulder_raise': 150,
        'elbow_curl': 160,
        'knee_bend': 150
    }
    
    target = target_angles.get(exercise_type, 150)
    
    for angle in angles.values():
        if angle >= target:
            total_score += 90
        elif angle >= target - 30:
            total_score += 70
        else:
            total_score += 50
    
    return total_score / len(angles)

def generate_feedback(performance_score):
    """Generate feedback text based on performance score"""
    if performance_score >= 80:
        return "🎉 Excellent form! Full range of motion achieved! Keep it up!"
    elif performance_score >= 60:
        return "💪 Good effort! Try to extend a bit more for better results."
    elif performance_score >= 40:
        return "📈 Keep practicing! Focus on reaching full extension."
    else:
        return "⚠️ Consider consulting a physiotherapist for guidance on proper form."
