import cv2
import mediapipe as mp
import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class HandTracker:
    """Track hand landmarks using MediaPipe"""
    
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=settings.MAX_NUM_HANDS,
            model_complexity=settings.MODEL_COMPLEXITY,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE
        )
        self.draw = mp.solutions.drawing_utils
        self.conn = mp.solutions.hands.HAND_CONNECTIONS
        self.draw_spec = mp.solutions.drawing_styles.get_default_hand_landmarks_style()

    def process(self, frame):
        """
        Process frame and detect hand landmarks
        
        Args:
            frame: BGR image from webcam
            
        Returns:
            Hand landmarks or None
        """
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.hands.process(rgb)

        # Draw and return landmarks if found
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            
            # Draw landmarks with connections
            self.draw.draw_landmarks(
                frame, 
                hand, 
                self.conn,
                self.draw_spec,
                mp.solutions.drawing_styles.get_default_hand_connections_style()
            )
            
            return hand
        
        return None
    
    def close(self):
        """Release MediaPipe resources"""
        self.hands.close()
