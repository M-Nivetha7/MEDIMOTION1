#!/usr/bin/env python3
"""
MediMotion Backend - Python 3.14 Compatible Version
"""

import os
import sys
import json
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

print("=" * 60)
print("MediMotion Backend Starting (Python 3.14 Compatible)")
print("=" * 60)
print(f"Python version: {sys.version}")

# Import with error handling
try:
    import numpy as np
    print(f"✓ NumPy version: {np.__version__}")
except ImportError as e:
    print(f"✗ NumPy import failed: {e}")
    sys.exit(1)

try:
    import cv2
    print(f"✓ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"✗ OpenCV import failed: {e}")
    sys.exit(1)

try:
    import mediapipe as mp
    print(f"✓ MediaPipe version: {mp.__version__}")
    MP_AVAILABLE = True
except ImportError as e:
    print(f"⚠ MediaPipe import failed: {e}")
    print("  Running in limited mode without pose detection")
    MP_AVAILABLE = False

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Create directories
os.makedirs('data', exist_ok=True)
os.makedirs('data/sessions', exist_ok=True)

# Initialize MediaPipe if available
if MP_AVAILABLE:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    try:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return float(angle)
    except Exception as e:
        print(f"Angle calculation error: {e}")
        return 0.0

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'numpy_version': np.__version__,
        'opencv_version': cv2.__version__,
        'mediapipe_available': MP_AVAILABLE,
        'message': 'MediMotion Backend is running on Python 3.14!'
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
        np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        angles = {}
        feedback_text = []
        performance_score = 50
        
        if MP_AVAILABLE:
            # Convert to RGB and process
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Get body points (MediaPipe landmark indices)
                # For more info: https://google.github.io/mediapipe/solutions/pose.html
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
                
                # Calculate based on exercise type
                if exercise_type == 'shoulder_raise':
                    angles['left_shoulder'] = calculate_angle(left_hip, left_shoulder, left_elbow)
                    angles['right_shoulder'] = calculate_angle(right_hip, right_shoulder, right_elbow)
                    target_angle = 150
                elif exercise_type == 'elbow_curl':
                    angles['left_elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    angles['right_elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    target_angle = 160
                elif exercise_type == 'knee_bend':
                    angles['left_knee'] = calculate_angle(left_hip, left_knee, left_ankle)
                    angles['right_knee'] = calculate_angle(right_hip, right_knee, right_ankle)
                    target_angle = 160
                else:
                    target_angle = 150
                
                # Generate feedback
                total_score = 0
                for joint, angle in angles.items():
                    if angle > target_angle:
                        feedback_text.append(f"✅ {joint.replace('_', ' ').title()}: Excellent! ({int(angle)}°)")
                        total_score += 90
                    elif angle > target_angle - 30:
                        feedback_text.append(f"💪 {joint.replace('_', ' ').title()}: Good form ({int(angle)}°)")
                        total_score += 70
                    else:
                        feedback_text.append(f"⚠️ {joint.replace('_', ' ').title()}: Need more extension ({int(angle)}°)")
                        total_score += 50
                
                if angles:
                    performance_score = total_score / len(angles)
                
                # Draw landmarks on frame
                mp_drawing.draw_landmarks(
                    frame, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # Add angle text to frame
                y_offset = 30
                for joint, angle in angles.items():
                    cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 30
                
                # Add performance score
                cv2.putText(frame, f'Score: {int(performance_score)}%', (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                overall_feedback = (
                    "🎉 Excellent work! Keep it up!" if performance_score > 80 else
                    "👍 Good progress! Keep practicing!" if performance_score > 60 else
                    "📈 Keep going! Try to extend more."
                )
            else:
                feedback_text.append("No pose detected. Please ensure you're fully visible.")
                overall_feedback = "Position yourself in front of the camera"
                cv2.putText(frame, "No pose detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # Fallback when MediaPipe is not available
            feedback_text.append("Pose detection is initializing...")
            overall_feedback = "System is ready. Start your exercise!"
            performance_score = 50
            cv2.putText(frame, "Ready for exercise", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Encode processed image
        _, buffer = cv2.imencode('.jpg', frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'feedback': {
                'overall_feedback': overall_feedback,
                'detailed_feedback': feedback_text if feedback_text else ["Keep up the good work!"],
                'performance_score': performance_score
            },
            'rep_count': 0,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        print(f"Error in analyze_pose: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_session', methods=['POST'])
def save_session():
    """Save exercise session"""
    try:
        data = request.json
        username = data.get('username', 'user')
        session_data = data.get('session_data', {})
        
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
        
        return jsonify({'message': 'Session saved successfully', 'total_sessions': len(sessions)})
        
    except Exception as e:
        print(f"Error saving session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_history/<username>', methods=['GET'])
def get_history(username):
    """Get user history"""
    try:
        filename = f'data/sessions/{username}_sessions.json'
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                sessions = json.load(f)
            return jsonify({'history': sessions, 'count': len(sessions)})
        else:
            return jsonify({'history': [], 'count': 0})
        
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'name': 'MediMotion Physiotherapy API',
        'version': '3.0.0',
        'python_version': sys.version.split()[0],
        'status': 'running',
        'endpoints': {
            'GET /': 'API information',
            'GET /api/health': 'Health check',
            'POST /api/analyze_pose': 'Analyze exercise pose',
            'POST /api/save_session': 'Save exercise session',
            'GET /api/get_history/<username>': 'Get user exercise history'
        }
    })

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🏥 MediMotion Physiotherapy Tracking System")
    print("=" * 60)
    print(f"\n✅ Python {sys.version.split()[0]} - Compatible")
    print(f"✅ NumPy {np.__version__}")
    print(f"✅ OpenCV {cv2.__version__}")
    print(f"✅ MediaPipe: {'Available' if MP_AVAILABLE else 'Limited Mode'}")
    
    print("\n📍 Server Information:")
    print(f"   URL: http://localhost:5000")
    print(f"   API Docs: http://localhost:5000/")
    
    print("\n📋 Available Endpoints:")
    print(f"   🌐 http://localhost:5000/ - API Info")
    print(f"   💚 http://localhost:5000/api/health - Health Check")
    print(f"   📊 http://localhost:5000/api/analyze_pose - Pose Analysis")
    print(f"   💾 http://localhost:5000/api/save_session - Save Session")
    print(f"   📜 http://localhost:5000/api/get_history/<username> - Get History")
    
    print("\n" + "=" * 60)
    print("🚀 Server is ready! Press Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)