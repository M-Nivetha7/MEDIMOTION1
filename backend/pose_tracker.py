import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class PoseTracker:
    def __init__(self):
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.rep_counter = 0
        self.rep_state = 'down'
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def get_landmark_coordinates(self, landmarks, width, height):
        """Extract coordinates for all important joints"""
        coords = {}
        
        # Shoulders
        coords['left_shoulder'] = [landmarks[11].x * width, landmarks[11].y * height]
        coords['right_shoulder'] = [landmarks[12].x * width, landmarks[12].y * height]
        
        # Elbows
        coords['left_elbow'] = [landmarks[13].x * width, landmarks[13].y * height]
        coords['right_elbow'] = [landmarks[14].x * width, landmarks[14].y * height]
        
        # Wrists
        coords['left_wrist'] = [landmarks[15].x * width, landmarks[15].y * height]
        coords['right_wrist'] = [landmarks[16].x * width, landmarks[16].y * height]
        
        # Hips
        coords['left_hip'] = [landmarks[23].x * width, landmarks[23].y * height]
        coords['right_hip'] = [landmarks[24].x * width, landmarks[24].y * height]
        
        # Knees
        coords['left_knee'] = [landmarks[25].x * width, landmarks[25].y * height]
        coords['right_knee'] = [landmarks[26].x * width, landmarks[26].y * height]
        
        # Ankles
        coords['left_ankle'] = [landmarks[27].x * width, landmarks[27].y * height]
        coords['right_ankle'] = [landmarks[28].x * width, landmarks[28].y * height]
        
        return coords
    
    def calculate_exercise_angles(self, coords, exercise_type):
        angles = {}
        
        if exercise_type == 'shoulder_raise':
            angles['Left Shoulder'] = self.calculate_angle(
                coords['left_hip'], coords['left_shoulder'], coords['left_elbow']
            )
            angles['Right Shoulder'] = self.calculate_angle(
                coords['right_hip'], coords['right_shoulder'], coords['right_elbow']
            )
        elif exercise_type == 'elbow_curl':
            angles['Left Elbow'] = self.calculate_angle(
                coords['left_shoulder'], coords['left_elbow'], coords['left_wrist']
            )
            angles['Right Elbow'] = self.calculate_angle(
                coords['right_shoulder'], coords['right_elbow'], coords['right_wrist']
            )
        elif exercise_type == 'knee_bend':
            angles['Left Knee'] = self.calculate_angle(
                coords['left_hip'], coords['left_knee'], coords['left_ankle']
            )
            angles['Right Knee'] = self.calculate_angle(
                coords['right_hip'], coords['right_knee'], coords['right_ankle']
            )
        
        return angles
    
    def draw_pose(self, frame, results):
        """Draw pose landmarks on frame"""
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        return frame
    
    def count_repetition(self, angles, exercise_type):
        """Count repetitions based on angle thresholds"""
        if not angles:
            return self.rep_counter
        
        # Get the primary angle for the exercise
        if exercise_type == 'shoulder_raise':
            primary_angle = angles.get('Left Shoulder', 0)
            down_threshold = 160
            up_threshold = 70
        elif exercise_type == 'elbow_curl':
            primary_angle = angles.get('Left Elbow', 0)
            down_threshold = 160
            up_threshold = 80
        elif exercise_type == 'knee_bend':
            primary_angle = angles.get('Left Knee', 0)
            down_threshold = 170
            up_threshold = 90
        else:
            return self.rep_counter
        
        # Rep counting logic
        if primary_angle > down_threshold and self.rep_state == 'up':
            self.rep_state = 'down'
        elif primary_angle < up_threshold and self.rep_state == 'down':
            self.rep_state = 'up'
            self.rep_counter += 1
        
        return self.rep_counter
    
    def reset_reps(self):
        self.rep_counter = 0
        self.rep_state = 'down'
