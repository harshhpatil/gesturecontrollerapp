import time
import cv2
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from camera.webcam import Webcam
from tracking.hand_tracker import HandTracker
from gestures.finger_state import get_finger_states, count_extended_fingers
from gestures.classifier import classify_gesture
from gestures.stabilizer import GestureStabilizer


def draw_debug_info(frame, hand, fingers, gesture, stable):
    """Draw comprehensive debug information on frame"""
    h, w = frame.shape[:2]
    
    # Background panel
    cv2.rectangle(frame, (10, 10), (400, 250), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (400, 250), (0, 255, 0), 2)
    
    y = 35
    spacing = 30
    
    # Title
    cv2.putText(frame, "GESTURE DEBUG", (20, y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    y += spacing
    
    # Separator
    cv2.line(frame, (20, y), (390, y), (0, 255, 0), 1)
    y += spacing
    
    # Finger states
    if fingers:
        for finger, state in fingers.items():
            color = (0, 255, 0) if state else (0, 0, 255)
            symbol = "UP" if state else "DOWN"
            cv2.putText(frame, f"{finger.capitalize()}: {symbol}", (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y += spacing
    
    # Separator
    y += 10
    cv2.line(frame, (20, y), (390, y), (0, 255, 0), 1)
    y += spacing
    
    # Gesture info
    cv2.putText(frame, f"Raw: {gesture}", (20, y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y += spacing
    
    cv2.putText(frame, f"Stable: {stable or 'WAITING...'}", (20, y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Hand landmarks info
    if hand:
        y = h - 60
        index_tip = hand.landmark[8]
        cv2.putText(frame, f"Index: ({index_tip.x:.3f}, {index_tip.y:.3f})", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        fingers_count = count_extended_fingers(fingers)
        cv2.putText(frame, f"Fingers Extended: {fingers_count}/5", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def main():
    """Run debug mode"""
    print("=" * 50)
    print("GESTURE DEBUG MODE")
    print("=" * 50)
    print("\nThis will show detailed gesture detection info")
    print("Press ESC to exit\n")
    
    try:
        cam = Webcam()
        tracker = HandTracker()
        stabilizer = GestureStabilizer()
        
        fps_start = time.time()
        fps_counter = 0
        fps = 0
        
        while cam.is_opened():
            frame = cam.read()
            if frame is None:
                break
            
            # Track FPS
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                fps = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Process hand
            hand = tracker.process(frame)
            
            fingers = None
            gesture = "NONE"
            stable = None
            
            if hand:
                fingers = get_finger_states(hand)
                gesture = classify_gesture(fingers)
                stable = stabilizer.update(gesture)
            
            # Draw debug info
            draw_debug_info(frame, hand, fingers, gesture, stable)
            
            # FPS
            cv2.putText(frame, f"FPS: {fps}", (frame.shape[1] - 120, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cam.show(frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cam.release()
        print("\nDebug session ended")


if __name__ == "__main__":
    main()