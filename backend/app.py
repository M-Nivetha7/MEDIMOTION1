import cv2
import mediapipe as mp
import numpy as np
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return angle if angle <= 180 else 360-angle

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        exercise_type = data.get('exercise_type', 'shoulder_raise')
        
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        
        angles = {}
        
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            h, w = frame.shape[:2]
            
            # Get coordinates
            ls = [lm[11].x*w, lm[11].y*h]
            rs = [lm[12].x*w, lm[12].y*h]
            le = [lm[13].x*w, lm[13].y*h]
            re = [lm[14].x*w, lm[14].y*h]
            lw = [lm[15].x*w, lm[15].y*h]
            rw = [lm[16].x*w, lm[16].y*h]
            lh = [lm[23].x*w, lm[23].y*h]
            rh = [lm[24].x*w, lm[24].y*h]
            lk = [lm[25].x*w, lm[25].y*h]
            rk = [lm[26].x*w, lm[26].y*h]
            la = [lm[27].x*w, lm[27].y*h]
            ra = [lm[28].x*w, lm[28].y*h]
            
            # Calculate angles
            if exercise_type == 'shoulder_raise':
                angles['Left Shoulder'] = calculate_angle(lh, ls, le)
                angles['Right Shoulder'] = calculate_angle(rh, rs, re)
            elif exercise_type == 'elbow_curl':
                angles['Left Elbow'] = calculate_angle(ls, le, lw)
                angles['Right Elbow'] = calculate_angle(rs, re, rw)
            else:
                angles['Left Knee'] = calculate_angle(lh, lk, la)
                angles['Right Knee'] = calculate_angle(rh, rk, ra)
            
            # Draw skeleton
            for connection in mp_pose.POSE_CONNECTIONS:
                start = (int(lm[connection[0]].x*w), int(lm[connection[0]].y*h))
                end = (int(lm[connection[1]].x*w), int(lm[connection[1]].y*h))
                cv2.line(frame, start, end, (0,255,0), 3)
            
            # Draw joints
            for i in range(33):
                x, y = int(lm[i].x*w), int(lm[i].y*h)
                cv2.circle(frame, (x,y), 6, (0,0,255), -1)
                cv2.circle(frame, (x,y), 8, (255,255,255), 2)
            
            # Add text
            y = 30
            for joint, angle in angles.items():
                cv2.putText(frame, f'{joint}: {int(angle)}°', (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                y += 30
        
        _, buffer = cv2.imencode('.jpg', frame)
        processed = base64.b64encode(buffer).decode()
        
        return jsonify({'angles': angles, 'processed_image': f'data:image/jpeg;base64,{processed}'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("✓ Server starting on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
