#!/usr/bin/env python3
"""
MediMotion Backend - Streaming Version for Real-time Tracking
Fixed for MediaPipe 0.10.35+
"""

import os
import sys
import json
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2

print("=" * 60)
print("MediMotion Real-time Tracking Server")
print("=" * 60)

# Import MediaPipe with compatibility handling
try:
    import mediapipe as mp
    print(f"✓ MediaPipe version: {mp.__version__}")
    
    # Try different import methods for compatibility
    if hasattr(mp, 'solutions'):
        print("✓ Using MediaPipe solutions API")
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    else:
        # For newer versions
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        print("✓ Using MediaPipe tasks API")
        # Create a pose landmarker
        base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO
        )
        pose = vision.PoseLandmarker.create_from_options(options)
        mp_drawing = None
except Exception as e:
    print(f"⚠ MediaPipe initialization warning: {e}")
    pose = None
    mp_drawing = None

app = Flask(__name__)
CORS(app)

os.makedirs('data', exist_ok=True)
os.makedirs('data/sessions', exist_ok=True)

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
    except:
        return 0.0

def draw_skeleton(frame, landmarks, angles):
    """Draw skeleton and angles on frame"""
    h, w = frame.shape[:2]
    
    # Define connections for skeleton
    connections = [
        (11, 12),  # shoulders
        (11, 13), (13, 15),  # left arm
        (12, 14), (14, 16),  # right arm
        (11, 23), (12, 24),  # torso
        (23, 24),  # hips
        (23, 25), (25, 27),  # left leg
        (24, 26), (26, 28),  # right leg
    ]
    
    # Draw connections
    for connection in connections:
        try:
            start = (int(landmarks[connection[0]].x * w), int(landmarks[connection[0]].y * h))
            end = (int(landmarks[connection[1]].x * w), int(landmarks[connection[1]].y * h))
            cv2.line(frame, start, end, (0, 255, 0), 2)
        except:
            pass
    
    # Draw landmarks (joints)
    for i, landmark in enumerate(landmarks):
        try:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), 1)
        except:
            pass
    
    # Add angle text
    y_offset = 30
    for joint, angle in angles.items():
        cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 30
    
    return frame

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'MediMotion Real-time Backend is running!'
    })

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
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
        performance_score = 50
        overall_feedback = "Starting pose detection..."
        
        # Process with MediaPipe if available
        if pose is not None:
            try:
                # Convert to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with available API
                if hasattr(mp, 'solutions'):
                    results = pose.process(rgb_frame)
                    if results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark
                        
                        # Calculate angles based on exercise
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
                        
                        if exercise_type == 'shoulder_raise':
                            angles['left_shoulder'] = calculate_angle(left_hip, left_shoulder, left_elbow)
                            angles['right_shoulder'] = calculate_angle(right_hip, right_shoulder, right_elbow)
                        elif exercise_type == 'elbow_curl':
                            angles['left_elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
                            angles['right_elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
                        elif exercise_type == 'knee_bend':
                            angles['left_knee'] = calculate_angle(left_hip, left_knee, left_ankle)
                            angles['right_knee'] = calculate_angle(right_hip, right_knee, right_ankle)
                        
                        # Draw skeleton
                        frame = draw_skeleton(frame, landmarks, angles)
                        
                        # Calculate performance score
                        total = 0
                        for angle in angles.values():
                            if angle > 150:
                                total += 90
                            elif angle > 120:
                                total += 70
                            else:
                                total += 50
                        
                        if angles:
                            performance_score = total / len(angles)
                        
                        if performance_score > 80:
                            overall_feedback = "Excellent form! Keep it up! 🎉"
                        elif performance_score > 60:
                            overall_feedback = "Good progress! Try to extend more 💪"
                        else:
                            overall_feedback = "Keep practicing! Focus on range of motion 📈"
                    else:
                        cv2.putText(frame, "No pose detected - Stand in front of camera", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        overall_feedback = "Position yourself in front of the camera"
            except Exception as e:
                print(f"Processing error: {e}")
                cv2.putText(frame, f"Processing...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "Camera ready - Start exercise", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            overall_feedback = "System ready! Press Start Exercise"
        
        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'feedback': {
                'overall_feedback': overall_feedback,
                'performance_score': performance_score
            },
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Server running on http://localhost:5000")
    print("📹 Ready for real-time pose tracking!")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)
