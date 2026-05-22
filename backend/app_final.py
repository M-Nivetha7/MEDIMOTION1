import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Try different MediaPipe import methods
try:
    import mediapipe as mp
    print(f"MediaPipe version: {mp.__version__}")
    
    # Check if solutions attribute exists
    if hasattr(mp, 'solutions'):
        print("Using mp.solutions API")
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
    else:
        # For newer versions
        print("Using alternative import method")
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        # Create a pose landmarker
        base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO
        )
        pose_detector = vision.PoseLandmarker.create_from_options(options)
        mp_pose = None
        mp_drawing = None
        
except ImportError as e:
    print(f"MediaPipe import error: {e}")
    mp_pose = None
    mp_drawing = None

app = Flask(__name__)
CORS(app)

# Initialize Pose
pose = None
if mp_pose:
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ MediaPipe Pose initialized")

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server running', 'mediapipe': pose is not None})

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
    try:
        data = request.json
        image_data = data['image']
        exercise_type = data.get('exercise_type', 'shoulder_raise')
        
        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        angles = {}
        
        if pose:
            # Process with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                h, w = frame.shape[:2]
                
                # Get landmark coordinates
                left_shoulder = [landmarks[11].x * w, landmarks[11].y * h]
                right_shoulder = [landmarks[12].x * w, landmarks[12].y * h]
                left_elbow = [landmarks[13].x * w, landmarks[13].y * h]
                right_elbow = [landmarks[14].x * w, landmarks[14].y * h]
                left_wrist = [landmarks[15].x * w, landmarks[15].y * h]
                right_wrist = [landmarks[16].x * w, landmarks[16].y * h]
                left_hip = [landmarks[23].x * w, landmarks[23].y * h]
                right_hip = [landmarks[24].x * w, landmarks[24].y * h]
                left_knee = [landmarks[25].x * w, landmarks[25].y * h]
                right_knee = [landmarks[26].x * w, landmarks[26].y * h]
                left_ankle = [landmarks[27].x * w, landmarks[27].y * h]
                right_ankle = [landmarks[28].x * w, landmarks[28].y * h]
                
                # Calculate angles
                if exercise_type == 'shoulder_raise':
                    angles['Left Shoulder'] = calculate_angle(left_hip, left_shoulder, left_elbow)
                    angles['Right Shoulder'] = calculate_angle(right_hip, right_shoulder, right_elbow)
                elif exercise_type == 'elbow_curl':
                    angles['Left Elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    angles['Right Elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
                elif exercise_type == 'knee_bend':
                    angles['Left Knee'] = calculate_angle(left_hip, left_knee, left_ankle)
                    angles['Right Knee'] = calculate_angle(right_hip, right_knee, right_ankle)
                
                # Draw skeleton - Draw lines between joints
                # Shoulder to shoulder
                cv2.line(frame, 
                        (int(landmarks[11].x * w), int(landmarks[11].y * h)),
                        (int(landmarks[12].x * w), int(landmarks[12].y * h)),
                        (0, 255, 0), 3)
                
                # Left arm
                cv2.line(frame,
                        (int(landmarks[11].x * w), int(landmarks[11].y * h)),
                        (int(landmarks[13].x * w), int(landmarks[13].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[13].x * w), int(landmarks[13].y * h)),
                        (int(landmarks[15].x * w), int(landmarks[15].y * h)),
                        (0, 255, 0), 3)
                
                # Right arm
                cv2.line(frame,
                        (int(landmarks[12].x * w), int(landmarks[12].y * h)),
                        (int(landmarks[14].x * w), int(landmarks[14].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[14].x * w), int(landmarks[14].y * h)),
                        (int(landmarks[16].x * w), int(landmarks[16].y * h)),
                        (0, 255, 0), 3)
                
                # Torso
                cv2.line(frame,
                        (int(landmarks[11].x * w), int(landmarks[11].y * h)),
                        (int(landmarks[23].x * w), int(landmarks[23].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[12].x * w), int(landmarks[12].y * h)),
                        (int(landmarks[24].x * w), int(landmarks[24].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[23].x * w), int(landmarks[23].y * h)),
                        (int(landmarks[24].x * w), int(landmarks[24].y * h)),
                        (0, 255, 0), 3)
                
                # Left leg
                cv2.line(frame,
                        (int(landmarks[23].x * w), int(landmarks[23].y * h)),
                        (int(landmarks[25].x * w), int(landmarks[25].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[25].x * w), int(landmarks[25].y * h)),
                        (int(landmarks[27].x * w), int(landmarks[27].y * h)),
                        (0, 255, 0), 3)
                
                # Right leg
                cv2.line(frame,
                        (int(landmarks[24].x * w), int(landmarks[24].y * h)),
                        (int(landmarks[26].x * w), int(landmarks[26].y * h)),
                        (0, 255, 0), 3)
                cv2.line(frame,
                        (int(landmarks[26].x * w), int(landmarks[26].y * h)),
                        (int(landmarks[28].x * w), int(landmarks[28].y * h)),
                        (0, 255, 0), 3)
                
                # Draw circles on joints
                for i in range(33):  # MediaPipe has 33 landmarks
                    x = int(landmarks[i].x * w)
                    y = int(landmarks[i].y * h)
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.circle(frame, (x, y), 7, (255, 255, 255), 2)
                
                # Add text
                y_offset = 30
                for joint, angle in angles.items():
                    cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 30
                
                # Calculate score
                score = 0
                for angle in angles.values():
                    if angle > 150:
                        score += 90
                    elif angle > 120:
                        score += 70
                    else:
                        score += 50
                if angles:
                    score = score / len(angles)
                
                cv2.putText(frame, f'Score: {int(score)}%', (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            else:
                cv2.putText(frame, 'No pose detected - Stand in front of camera', (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            cv2.putText(frame, 'MediaPipe not available', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Encode image
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("MediMotion Backend Server")
    print("="*50)
    print(f"MediaPipe available: {pose is not None}")
    print("Server running on http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
