class FeedbackGenerator:
    def __init__(self):
        self.exercise_ranges = {
            'shoulder_raise': {
                'left_shoulder': {'min': 0, 'max': 180, 'ideal_min': 150, 'ideal_max': 180},
                'right_shoulder': {'min': 0, 'max': 180, 'ideal_min': 150, 'ideal_max': 180}
            },
            'elbow_curl': {
                'left_elbow': {'min': 0, 'max': 180, 'ideal_min': 160, 'ideal_max': 180},
                'right_elbow': {'min': 0, 'max': 180, 'ideal_min': 160, 'ideal_max': 180}
            },
            'knee_bend': {
                'left_knee': {'min': 0, 'max': 180, 'ideal_min': 150, 'ideal_max': 170},
                'right_knee': {'min': 0, 'max': 180, 'ideal_min': 150, 'ideal_max': 170}
            },
            'squat': {
                'left_knee': {'min': 0, 'max': 180, 'ideal_min': 90, 'ideal_max': 120},
                'right_knee': {'min': 0, 'max': 180, 'ideal_min': 90, 'ideal_max': 120}
            }
        }
        
    def check_form(self, angles, exercise_type):
        """Check if the exercise form is correct and provide feedback"""
        feedback = []
        score = 0
        total_points = len(angles) * 10
        
        for joint, angle in angles.items():
            if exercise_type in self.exercise_ranges:
                range_data = self.exercise_ranges[exercise_type].get(joint)
                if range_data:
                    if range_data['ideal_min'] <= angle <= range_data['ideal_max']:
                        feedback.append(f"✅ {joint}: Perfect form! Angle: {int(angle)}°")
                        score += 10
                    elif angle > range_data['max']:
                        feedback.append(f"⚠️ {joint}: Too much extension. Aim for {range_data['ideal_max']}°")
                        score += 5
                    elif angle < range_data['min']:
                        feedback.append(f"⚠️ {joint}: Need more extension. Aim for {range_data['ideal_min']}°")
                        score += 3
                    else:
                        feedback.append(f"💪 {joint}: Good effort! Keep practicing. Current: {int(angle)}°")
                        score += 7
        
        performance_score = (score / total_points) * 100 if total_points > 0 else 0
        
        # Overall feedback
        if performance_score >= 80:
            overall = "Excellent form! Keep up the great work! 🎉"
        elif performance_score >= 60:
            overall = "Good progress! Focus on improving your range of motion. 💪"
        elif performance_score >= 40:
            overall = "Keep practicing! Try to extend further in your movements. ⚠️"
        else:
            overall = "Consider consulting a physiotherapist for guidance. 📋"
            
        return {
            'detailed_feedback': feedback,
            'performance_score': performance_score,
            'overall_feedback': overall
        }