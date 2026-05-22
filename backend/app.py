from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import base64
import numpy as np
from utils import save_session_data, get_user_history, calculate_performance_score, generate_feedback
from auth import AuthManager
from pose_tracker import PoseTracker
from report import generate_pdf_report

app = Flask(__name__)
CORS(app)

# Initialize components
auth_manager = AuthManager()
pose_tracker = PoseTracker()

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'MediMotion API is running'})

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
    try:
        data = request.json
        image_data = data['image']
        exercise_type = data.get('exercise_type', 'shoulder_raise')
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        angles = {}
        
        if results.pose_landmarks:
            h, w = frame.shape[:2]
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            coords = pose_tracker.get_landmark_coordinates(landmarks, w, h)
            
            # Calculate angles
            angles = pose_tracker.calculate_exercise_angles(coords, exercise_type)
            
            # Count repetitions
            rep_count = pose_tracker.count_repetition(angles, exercise_type)
            
            # Draw skeleton
            pose_tracker.draw_pose(frame, results)
            
            # Add angle text
            y = 30
            for joint, angle in angles.items():
                cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y += 30
            
            cv2.putText(frame, f'Reps: {rep_count}', (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        _, buffer = cv2.imencode('.jpg', frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'rep_count': pose_tracker.rep_counter,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_session', methods=['POST'])
def save_session():
    try:
        data = request.json
        username = data.get('username')
        session_data = data.get('session_data')
        save_session_data(username, session_data)
        return jsonify({'message': 'Session saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_history/<username>', methods=['GET'])
def get_history(username):
    try:
        history = get_user_history(username)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏥 MediMotion Backend Server")
    print("="*50)
    print("Server running on http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
