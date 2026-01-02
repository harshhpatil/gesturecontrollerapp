from collections import deque
import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class SwipeDetector:
    """Detect horizontal swipe gestures"""
    
    def __init__(self):
        self.x = deque(maxlen=settings.SWIPE_BUFFER_SIZE)
        self.threshold = settings.SWIPE_THRESHOLD
        self.last_swipe_time = 0
        self.cooldown = 0.5  # Seconds between swipes

    def update(self, tip):
        """
        Update position buffer and detect swipe
        
        Args:
            tip: Fingertip landmark with x coordinate
            
        Returns:
            "LEFT", "RIGHT", or None
        """
        import time
        
        self.x.append(tip.x)
        
        # Need full buffer for detection
        if len(self.x) < self.x.maxlen:
            return None
        
        # Check cooldown
        if time.time() - self.last_swipe_time < self.cooldown:
            return None

        # Calculate horizontal displacement
        dx = self.x[-1] - self.x[0]

        # Detect swipe direction
        if dx > self.threshold:
            self.last_swipe_time = time.time()
            self.x.clear()  # Clear buffer after detection
            return "RIGHT"
        elif dx < -self.threshold:
            self.last_swipe_time = time.time()
            self.x.clear()  # Clear buffer after detection
            return "LEFT"
        
        return None
    
    def reset(self):
        """Clear position buffer"""
        self.x.clear()
