def generate_feedback(angles_data=None):
    """
    Generates simple AI-style feedback based on detected joint angles.
    If no angle data is provided, returns a general feedback string.
    """
    
    if not angles_data or not isinstance(angles_data, dict):
        return "⚙️ Keep a steady posture and maintain consistent movement during exercise."
    
    feedbacks = []
    performance_score = 0
    
    for joint, angle in angles_data.items():
        if angle < 30:
            feedbacks.append(f"🦵 {joint}: Try to extend more — your angle is only {angle:.1f}°.")
            performance_score += 30
        elif angle < 90:
            feedbacks.append(f"⚠️ {joint}: Partial range of motion. Aim for higher extension. Current: {angle:.1f}°")
            performance_score += 50
        elif angle > 150:
            feedbacks.append(f"💪 {joint}: Great flexibility! {angle:.1f}° looks perfect.")
            performance_score += 90
        elif angle > 120:
            feedbacks.append(f"✅ {joint}: Good form maintained at {angle:.1f}°.")
            performance_score += 75
        else:
            feedbacks.append(f"📈 {joint}: Keep working on range of motion. Current: {angle:.1f}°")
            performance_score += 60
    
    if angles_data:
        performance_score = performance_score / len(angles_data)
    
    # Overall assessment
    if performance_score >= 80:
        overall = "🎉 Excellent! You're doing great! Keep up the perfect form!"
    elif performance_score >= 60:
        overall = "👍 Good progress! Focus on extending your movements further."
    elif performance_score >= 40:
        overall = "📚 Keep practicing! Try to achieve a fuller range of motion."
    else:
        overall = "📋 Consider slower movements and focus on form before increasing range."
    
    return {
        'detailed_feedback': feedbacks,
        'overall_feedback': overall,
        'performance_score': performance_score
    }
