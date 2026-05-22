import cv2
import mediapipe as mp
import numpy as np
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

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
    return jsonify({'status': 'ok', 'message': 'Server running'})

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
        
        # Process with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        angles = {}
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get landmark coordinates
            h, w = frame.shape[:2]
            
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * w,
                            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * h]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w,
                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * w,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * h]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * w,
                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * h]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                      landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * w,
                       landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * h]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                       landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * w,
                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * h]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w,
                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * w,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * h]
            
            # Calculate angles based on exercise
            if exercise_type == 'shoulder_raise':
                angles['Left Shoulder'] = calculate_angle(left_hip, left_shoulder, left_elbow)
                angles['Right Shoulder'] = calculate_angle(right_hip, right_shoulder, right_elbow)
            elif exercise_type == 'elbow_curl':
                angles['Left Elbow'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
                angles['Right Elbow'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
            elif exercise_type == 'knee_bend':
                angles['Left Knee'] = calculate_angle(left_hip, left_knee, left_ankle)
                angles['Right Knee'] = calculate_angle(right_hip, right_knee, right_ankle)
            
            # Draw pose landmarks with custom styling
            # Draw connections with thicker green lines
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Override to make lines thicker and more visible
            connections = mp_pose.POSE_CONNECTIONS
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                start_point = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                end_point = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                cv2.line(frame, start_point, end_point, (0, 255, 0), 3)
            
            # Draw circles on joints
            for landmark in landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                cv2.circle(frame, (x, y), 7, (255, 255, 255), 2)
            
            # Add angle text on image
            y_offset = 30
            for joint, angle in angles.items():
                cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 30
            
            # Calculate performance score
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
        
        # Encode image
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'angles': angles,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
