#!/usr/bin/env python3
"""
MediMotion Backend Server
"""

import sys
import os
import json
import base64
from datetime import datetime
import traceback

# Try to import required modules with error handling
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    print("✓ Flask imported")
except ImportError as e:
    print(f"✗ Failed to import Flask: {e}")
    print("\nPlease install Flask using:")
    print("pip install flask flask-cors")
    sys.exit(1)

try:
    import cv2
    print("✓ OpenCV imported")
except ImportError as e:
    print(f"✗ Failed to import OpenCV: {e}")
    print("\nPlease install OpenCV using:")
    print("pip install opencv-python")
    sys.exit(1)

try:
    import mediapipe as mp
    print("✓ MediaPipe imported")
except ImportError as e:
    print(f"✗ Failed to import MediaPipe: {e}")
    print("\nPlease install MediaPipe using:")
    print("pip install mediapipe")
    sys.exit(1)

try:
    import numpy as np
    print("✓ NumPy imported")
except ImportError as e:
    print(f"✗ Failed to import NumPy: {e}")
    print("\nPlease install NumPy using:")
    print("pip install numpy")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('data/sessions', exist_ok=True)
os.makedirs('data/reports', exist_ok=True)

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'flask': True,
            'opencv': True,
            'mediapipe': True,
            'numpy': True
        }
    })

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
    """Analyze pose from image"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        exercise_type = data.get('exercise_type', 'shoulder_raise')
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return jsonify({
                'angles': {},
                'feedback': {'overall_feedback': 'No pose detected. Please ensure you are fully visible in frame.'},
                'rep_count': 0,
                'processed_image': image_data
            }), 200
        
        # Extract landmarks
        landmarks = results.pose_landmarks.landmark
        
        # Get relevant landmarks
        left_shoulder = [landmarks[11].x, landmarks[11].y]
        right_shoulder = [landmarks[12].x, landmarks[12].y]
        left_elbow = [landmarks[13].x, landmarks[13].y]
        right_elbow = [landmarks[14].x, landmarks[14].y]
        left_wrist = [landmarks[15].x, landmarks[15].y]
        right_wrist = [landmarks[16].x, landmarks[16].y]
        left_hip = [landmarks[23].x, landmarks[23].y]
        right_hip = [landmarks[24].x, landmarks[24].y]
        left_knee = [landmarks[25].x, landmarks[25].y]
        right_knee = [landmarks[26].x, landmarks[26].y]
        left_ankle = [landmarks[27].x, landmarks[27].y]
        right_ankle = [landmarks[28].x, landmarks[28].y]
        
        angles = {}
        
        # Calculate angles based on exercise type
        if exercise_type == 'shoulder_raise':
            angles['left_shoulder'] = calculate_angle(left_hip, left_shoulder, left_elbow)
            angles['right_shoulder'] = calculate_angle(right_hip, right_shoulder, right_elbow)
        elif exercise_type == 'elbow_curl':
            angles['left_elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
            angles['right_elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
        elif exercise_type == 'knee_bend':
            angles['left_knee'] = calculate_angle(left_hip, left_knee, left_ankle)
            angles['right_knee'] = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Generate feedback
        feedback_text = []
        for joint, angle in angles.items():
            if angle > 160:
                feedback_text.append(f"✅ {joint}: Excellent form!")
            elif angle > 120:
                feedback_text.append(f"💪 {joint}: Good, try to extend more")
            else:
                feedback_text.append(f"⚠️ {joint}: Need more extension")
        
        # Draw landmarks on image
        annotated_image = frame.copy()
        mp_drawing.draw_landmarks(
            annotated_image, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        
        # Add angle text
        y_offset = 30
        for joint, angle in angles.items():
            cv2.putText(annotated_image, f'{joint}: {int(angle)}°', (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 30
        
        # Convert back to base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'feedback': {
                'overall_feedback': ' '.join(feedback_text),
                'detailed_feedback': feedback_text,
                'performance_score': 75
            },
            'rep_count': 0,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        print(f"Error in analyze_pose: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_session', methods=['POST'])
def save_session():
    """Save exercise session"""
    try:
        data = request.json
        username = data.get('username')
        session_data = data.get('session_data')
        
        filename = f'data/sessions/{username}_sessions.json'
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                sessions = json.load(f)
        else:
            sessions = []
        
        sessions.append({
            'timestamp': datetime.now().isoformat(),
            'data': session_data
        })
        
        with open(filename, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return jsonify({'message': 'Session saved successfully'})
        
    except Exception as e:
        print(f"Error in save_session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_history/<username>', methods=['GET'])
def get_history(username):
    """Get user history"""
    try:
        filename = f'data/sessions/{username}_sessions.json'
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                sessions = json.load(f)
            return jsonify({'history': sessions})
        else:
            return jsonify({'history': []})
        
    except Exception as e:
        print(f"Error in get_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("MediMotion Backend Server")
    print("=" * 50)
    print("\nServer Information:")
    print(f"  - Host: 0.0.0.0")
    print(f"  - Port: 5000")
    print(f"  - URL: http://localhost:5000")
    print("\nAvailable Endpoints:")
    print(f"  - GET  /api/health")
    print(f"  - POST /api/analyze_pose")
    print(f"  - POST /api/save_session")
    print(f"  - GET  /api/get_history/<username>")
    print("\n" + "=" * 50)
    print("\nStarting server...\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')