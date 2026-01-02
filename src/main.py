import time
import cv2
import sys
from pathlib import Path

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

from camera.webcam import Webcam
from tracking.hand_tracker import HandTracker
from gestures.finger_state import get_finger_states
from gestures.classifier import classify_gesture
from gestures.stabilizer import GestureStabilizer
from gestures.swipe import SwipeDetector
from actions.mouse_controller import MouseController


class FPSCounter:
    """Track and display FPS"""
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
    
    def update(self):
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps


def main():
    """Main application loop"""
    try:
        # Initialize components
        cam = Webcam(index=settings.CAMERA_INDEX)
        tracker = HandTracker()
        stabilizer = GestureStabilizer()
        swipe = SwipeDetector()
        mouse = MouseController()
        fps_counter = FPSCounter()

        # State variables
        paused = False
        pause_time = 0
        frame_count = 0
        drag_start = 0

        print("Gesture Control Started!")
        print("Press ESC to exit")
        print("-" * 40)

        while cam.is_opened():
            frame = cam.read()
            if frame is None:
                print("Failed to read frame")
                break

            frame_count += 1

            # Process hand tracking every frame
            try:
                hand = tracker.process(frame)
            except Exception as e:
                print(f"Hand tracking error: {e}")
                hand = None

            if hand:
                fingers = get_finger_states(hand)
                gesture = classify_gesture(fingers)
                stable = stabilizer.update(gesture)

                # Handle pause toggle
                if stable == "PAUSE":
                    if time.time() - pause_time > settings.PAUSE_COOLDOWN:
                        paused = not paused
                        pause_time = time.time()
                        print(f"{'Paused' if paused else 'Resumed'}")

                # Execute gestures when not paused
                if not paused and stable:
                    try:
                        if stable == "MOVE":
                            drag_start = 0
                            mouse.move(hand)

                            # Check for swipe
                            swipe_dir = swipe.update(hand.landmark[8])
                            if swipe_dir:
                                mouse.swipe(swipe_dir)
                                print(f"Swipe: {swipe_dir}")

                        elif stable == "CLICK":
                            drag_start = 0
                            mouse.click()

                        elif stable == "DRAG":
                            if drag_start == 0:
                                drag_start = time.time()
                            elif time.time() - drag_start > settings.DRAG_HOLD_TIME:
                                mouse.drag(hand)

                        elif stable == "SCROLL":
                            drag_start = 0
                            mouse.scroll(hand)

                        else:
                            drag_start = 0
                            mouse.release()
                    except Exception as e:
                        print(f"Action error: {e}")
                        mouse.release()
                else:
                    drag_start = 0
                    mouse.release()

                # Display info on frame
                status_color = (0, 255, 255) if paused else (0, 255, 0)
                cv2.putText(frame, f"Gesture: {stable or 'NONE'}", (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Status: {'PAUSED' if paused else 'ACTIVE'}", 
                           (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            # FPS counter
            if settings.SHOW_FPS:
                fps = fps_counter.update()
                cv2.putText(frame, f"FPS: {fps:.1f}", (20, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Display frame (with optional frame skip for performance)
            if frame_count % settings.FRAME_SKIP == 0:
                cam.show(frame)

            # Check for ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                print("Exiting...")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        mouse.release()
        cam.release()
        print("Cleanup complete")


if __name__ == "__main__":
    main() 