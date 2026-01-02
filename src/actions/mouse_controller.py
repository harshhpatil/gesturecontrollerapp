import pyautogui
import time
import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings

# Disable PyAutoGUI safety features for smooth control
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class MouseController:
    """Control mouse actions based on hand gestures"""
    
    def __init__(self):
        self.w, self.h = pyautogui.size()
        self.dragging = False
        self.last_click = 0
        
        # Initialize cursor position to center
        self.px, self.py = self.w // 2, self.h // 2

    def move(self, hand):
        """Move cursor based on index finger position"""
        tip = hand.landmark[8]

        # Convert normalized coordinates to screen space
        # Flip X for mirror effect
        tx = int((1 - tip.x) * self.w)
        ty = int(tip.y * self.h)

        # Apply exponential smoothing
        x = int(self.px + (tx - self.px) * settings.CURSOR_SMOOTHING)
        y = int(self.py + (ty - self.py) * settings.CURSOR_SMOOTHING)

        # Move cursor
        try:
            pyautogui.moveTo(x, y, _pause=False)
            self.px, self.py = x, y
        except Exception as e:
            print(f"Move error: {e}")

    def click(self):
        """Perform left click with cooldown"""
        now = time.time()
        if now - self.last_click > settings.CLICK_COOLDOWN:
            try:
                pyautogui.click()
                self.last_click = now
            except Exception as e:
                print(f"Click error: {e}")

    def drag(self, hand):
        """Drag while moving cursor"""
        if not self.dragging:
            try:
                pyautogui.mouseDown()
                self.dragging = True
            except Exception as e:
                print(f"Drag start error: {e}")
        self.move(hand)

    def release(self):
        """Release mouse button if dragging"""
        if self.dragging:
            try:
                pyautogui.mouseUp()
                self.dragging = False
            except Exception as e:
                print(f"Release error: {e}")

    def scroll(self, hand):
        """Scroll based on vertical finger movement"""
        # Calculate vertical movement between fingertips
        dy = hand.landmark[8].y - hand.landmark[6].y

        # Apply dead zone to prevent jitter
        if abs(dy) < settings.SCROLL_DEADZONE:
            return

        # Calculate scroll amount with limits
        amount = dy * settings.SCROLL_MULTIPLIER
        amount = max(min(amount, settings.SCROLL_MAX_AMOUNT), 
                    -settings.SCROLL_MAX_AMOUNT)
        
        try:
            # Negative for natural scrolling direction
            pyautogui.scroll(-int(amount))
        except Exception as e:
            print(f"Scroll error: {e}")

    def swipe(self, direction):
        """Navigate browser back/forward"""
        try:
            if direction == "LEFT":
                pyautogui.hotkey("alt", "left")
            elif direction == "RIGHT":
                pyautogui.hotkey("alt", "right")
        except Exception as e:
            print(f"Swipe error: {e}")

