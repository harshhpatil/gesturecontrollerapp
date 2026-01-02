def get_finger_states(hand):
    """
    Detect which fingers are extended
    
    Args:
        hand: MediaPipe hand landmarks
        
    Returns:
        Dictionary with boolean state for each finger
    """
    lm = hand.landmark
    
    # Improved thumb detection (works for both hands)
    # Check if thumb tip is far from palm center
    palm_x = lm[0].x
    thumb_extended = abs(lm[4].x - palm_x) > abs(lm[3].x - palm_x)
    
    return {
        "thumb":  thumb_extended,
        "index":  lm[8].y < lm[6].y,   # Tip above middle joint
        "middle": lm[12].y < lm[10].y,
        "ring":   lm[16].y < lm[14].y,
        "pinky":  lm[20].y < lm[18].y,
    }


def count_extended_fingers(finger_states):
    """
    Count how many fingers are extended
    
    Args:
        finger_states: Dictionary from get_finger_states
        
    Returns:
        Number of extended fingers
    """
    return sum(finger_states.values())
