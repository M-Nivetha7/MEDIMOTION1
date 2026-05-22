import numpy as np
import json
import os
from datetime import datetime

class PoseAnalyzer:
    def __init__(self):
        self.rep_states = {}
        self.session_data = {}
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def calculate_exercise_angles(self, landmarks, exercise_type):
        """Calculate specific angles based on exercise type"""
        angles = {}
        
        # Get landmark coordinates
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
            # Left shoulder angle
            angles['left_shoulder'] = self.calculate_angle(left_hip, left_shoulder, left_elbow)
            # Right shoulder angle
            angles['right_shoulder'] = self.calculate_angle(right_hip, right_shoulder, right_elbow)
            
        elif exercise_type == 'elbow_curl':
            # Left elbow angle
            angles['left_elbow'] = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            # Right elbow angle
            angles['right_elbow'] = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
        elif exercise_type == 'knee_bend':
            # Left knee angle
            angles['left_knee'] = self.calculate_angle(left_hip, left_knee, left_ankle)
            # Right knee angle
            angles['right_knee'] = self.calculate_angle(right_hip, right_knee, right_ankle)
            
        elif exercise_type == 'squat':
            angles['left_knee'] = self.calculate_angle(left_hip, left_knee, left_ankle)
            angles['right_knee'] = self.calculate_angle(right_hip, right_knee, right_ankle)
            angles['left_hip'] = self.calculate_angle(left_shoulder, left_hip, left_knee)
            angles['right_hip'] = self.calculate_angle(right_shoulder, right_hip, right_knee)
            
        return angles
    
    def count_repetition(self, angles, exercise_type):
        """Count repetitions based on angle thresholds"""
        key_angle = None
        
        if exercise_type == 'shoulder_raise':
            key_angle = angles.get('left_shoulder', 0)
        elif exercise_type == 'elbow_curl':
            key_angle = angles.get('left_elbow', 0)
        elif exercise_type == 'knee_bend':
            key_angle = angles.get('left_knee', 0)
            
        if key_angle is None:
            return 0
            
        session_key = f"{exercise_type}_rep_count"
        
        if session_key not in self.rep_states:
            self.rep_states[session_key] = {'count': 0, 'state': 'down'}
            
        state = self.rep_states[session_key]
        
        # Rep counting logic
        if exercise_type in ['shoulder_raise', 'elbow_curl']:
            if key_angle > 160 and state['state'] == 'up':
                state['state'] = 'down'
            elif key_angle < 70 and state['state'] == 'down':
                state['state'] = 'up'
                state['count'] += 1
        else:  # knee_bend
            if key_angle > 170 and state['state'] == 'down':
                state['state'] = 'up'
            elif key_angle < 90 and state['state'] == 'up':
                state['state'] = 'down'
                state['count'] += 1
                
        return state['count']
    
    def save_session_data(self, username, session_data):
        """Save exercise session data"""
        os.makedirs('data/sessions', exist_ok=True)
        filename = f'data/sessions/{username}_sessions.json'
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = []
            
        data.append({
            'timestamp': datetime.now().isoformat(),
            'data': session_data
        })
        
        with open(filename, 'w') as f:
            json.dump(data, f)
            
    def get_user_history(self, username):
        """Get user exercise history"""
        filename = f'data/sessions/{username}_sessions.json'
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return []