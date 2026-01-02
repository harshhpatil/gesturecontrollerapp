from collections import deque
import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class GestureStabilizer:
    """Stabilize gesture detection by requiring consistency"""
    
    def __init__(self):
        self.buf = deque(maxlen=settings.GESTURE_BUFFER_SIZE)
        self.threshold = settings.GESTURE_THRESHOLD
        self.last_stable = None

    def update(self, gesture):
        """
        Update buffer and return stable gesture
        
        Args:
            gesture: Current detected gesture
            
        Returns:
            Stable gesture if threshold met, otherwise last stable gesture
        """
        self.buf.append(gesture)
        
        # Check if current gesture appears enough times
        if self.buf.count(gesture) >= self.threshold:
            self.last_stable = gesture
            return gesture
        
        # Return last stable gesture to avoid None
        return self.last_stable
    
    def reset(self):
        """Clear buffer and reset state"""
        self.buf.clear()
        self.last_stable = None