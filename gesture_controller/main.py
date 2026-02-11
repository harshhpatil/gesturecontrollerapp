"""Main application module for gesture controller."""

import sys
import time
from typing import Optional

import cv2

from .config import Config
from .control_mapper import ControlMapper
from .gesture_recognizer import GestureRecognizer
from .hand_detector import HandDetector
from .os_controller import OSController


class GestureController:
    """Main gesture controller application."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize gesture controller.

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

        # Initialize components
        self.hand_detector = HandDetector(self.config)
        self.gesture_recognizer = GestureRecognizer(self.config)
        self.control_mapper = ControlMapper(self.config)
        self.os_controller = OSController(self.config)

        # Camera setup
        self.camera = None
        self.is_running = False
        self.is_paused = False

        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

        # State management
        self.last_pause_time = 0
        self.drag_start_time = 0
        self.last_scroll_y = None

    def initialize_camera(self) -> bool:
        """Initialize webcam capture.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.config.CAMERA_INDEX)

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)

            if not self.camera.isOpened():
                print("Error: Could not open camera")
                return False

            print(f"Camera initialized: {self.config.CAMERA_WIDTH}x{self.config.CAMERA_HEIGHT}")
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False

    def process_frame(self, frame):
        """Process a single frame.

        Args:
            frame: Camera frame to process

        Returns:
            Processed frame with annotations
        """
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)

        # Detect hands
        hands_found, hand_landmarks_list = self.hand_detector.detect_hands(frame)

        if not hands_found or not hand_landmarks_list:
            # No hands detected
            if self.config.SHOW_GESTURES:
                self._draw_status(frame, "No hand detected", (0, 0, 255))
            return frame

        # Get first hand
        hand_landmarks = hand_landmarks_list[0]

        # Draw landmarks if enabled
        if self.config.SHOW_LANDMARKS:
            self.hand_detector.draw_landmarks(frame, hand_landmarks)

        # Get finger states
        finger_states = self.hand_detector.get_finger_states(hand_landmarks)

        # Recognize gesture
        gesture = self.gesture_recognizer.recognize_gesture(
            finger_states, hand_landmarks, self.hand_detector
        )

        # Stabilize gesture
        stable_gesture = self.gesture_recognizer.stabilize_gesture(gesture)

        # Display current gesture
        if self.config.SHOW_GESTURES and stable_gesture:
            self._draw_gesture(frame, stable_gesture)

        # Execute actions if not paused
        if not self.is_paused:
            self._execute_gesture_action(stable_gesture, hand_landmarks, finger_states)
        else:
            # Release drag if paused
            self.os_controller.stop_drag()

        # Check for pause toggle
        if stable_gesture == "THUMBS_UP":
            self._toggle_pause()

        # Display pause status
        status_text = "PAUSED" if self.is_paused else "ACTIVE"
        status_color = (0, 255, 255) if self.is_paused else (0, 255, 0)
        self._draw_status(frame, status_text, status_color)

        return frame

    def _execute_gesture_action(self, gesture: str, hand_landmarks, finger_states: dict) -> None:
        """Execute action based on recognized gesture.

        Args:
            gesture: Recognized gesture
            hand_landmarks: Hand landmarks object
            finger_states: Dictionary of finger states
        """
        if not gesture or gesture == "IDLE":
            self.os_controller.stop_drag()
            self.drag_start_time = 0
            return

        # Map gesture to action
        action = self.control_mapper.map_gesture_to_action(gesture)

        if action == "move_cursor":
            # Move cursor based on index finger
            index_tip = self.hand_detector.get_normalized_landmark(hand_landmarks, 8)
            if index_tip:
                self.os_controller.move_cursor(index_tip[0], index_tip[1])

            # Check for swipe
            swipe = self.gesture_recognizer.detect_swipe(hand_landmarks, self.hand_detector)
            if swipe:
                swipe_action = self.control_mapper.map_swipe_to_action(swipe)
                if swipe_action:
                    self._execute_swipe_action(swipe_action)

        elif action == "left_click":
            self.os_controller.left_click()
            self.os_controller.stop_drag()

        elif action == "right_click":
            self.os_controller.right_click()
            self.os_controller.stop_drag()

        elif action == "double_click":
            self.os_controller.double_click()
            self.os_controller.stop_drag()

        elif action == "drag":
            # Start drag after hold time
            if self.drag_start_time == 0:
                self.drag_start_time = time.time()
            elif time.time() - self.drag_start_time > self.config.DRAG_HOLD_TIME:
                self.os_controller.start_drag()
                # Move cursor while dragging
                index_tip = self.hand_detector.get_normalized_landmark(hand_landmarks, 8)
                if index_tip:
                    self.os_controller.move_cursor(index_tip[0], index_tip[1])

        elif action == "scroll":
            # Scroll based on vertical hand movement
            index_tip = self.hand_detector.get_normalized_landmark(hand_landmarks, 8)
            if index_tip:
                current_y = index_tip[1]

                if self.last_scroll_y is not None:
                    dy = current_y - self.last_scroll_y

                    # Check deadzone
                    if abs(dy) > self.config.SCROLL_DEADZONE:
                        # Convert to scroll amount
                        scroll_amount = int(dy * 100)
                        self.os_controller.scroll(scroll_amount)

                self.last_scroll_y = current_y

        else:
            # Reset states for unknown actions
            self.os_controller.stop_drag()
            self.drag_start_time = 0

    def _execute_swipe_action(self, action: str) -> None:
        """Execute swipe action.

        Args:
            action: Swipe action name
        """
        if action == "navigate_back":
            self.os_controller.navigate_back()
        elif action == "navigate_forward":
            self.os_controller.navigate_forward()
        elif action == "volume_up":
            self.os_controller.volume_up()
        elif action == "volume_down":
            self.os_controller.volume_down()

    def _toggle_pause(self) -> None:
        """Toggle pause state with cooldown."""
        current_time = time.time()
        if current_time - self.last_pause_time > 1.0:  # 1 second cooldown
            self.is_paused = not self.is_paused
            self.last_pause_time = current_time
            print(f"Gesture controller {'PAUSED' if self.is_paused else 'RESUMED'}")

    def _draw_gesture(self, frame, gesture: str) -> None:
        """Draw gesture name on frame.

        Args:
            frame: Frame to draw on
            gesture: Gesture name
        """
        cv2.putText(
            frame,
            f"Gesture: {gesture}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

    def _draw_status(self, frame, status: str, color: tuple) -> None:
        """Draw status text on frame.

        Args:
            frame: Frame to draw on
            status: Status text
            color: Text color (BGR)
        """
        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    def _update_fps(self) -> None:
        """Update FPS counter."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()

    def _draw_fps(self, frame) -> None:
        """Draw FPS on frame.

        Args:
            frame: Frame to draw on
        """
        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2,
        )

    def run(self) -> None:
        """Run the gesture controller application."""
        # Initialize camera
        if not self.initialize_camera():
            return

        self.is_running = True

        print("=" * 50)
        print("Gesture Controller Started!")
        print("=" * 50)
        print("Controls:")
        print("  - Thumbs Up: Pause/Resume")
        print("  - ESC: Exit")
        print("=" * 50)

        try:
            while self.is_running:
                # Read frame
                ret, frame = self.camera.read()

                if not ret:
                    print("Error: Failed to read frame")
                    break

                # Process frame
                processed_frame = self.process_frame(frame)

                # Update and draw FPS
                if self.config.SHOW_FPS:
                    self._update_fps()
                    self._draw_fps(processed_frame)

                # Display frame
                if self.frame_count % self.config.FRAME_SKIP == 0:
                    cv2.imshow(self.config.WINDOW_NAME, processed_frame)

                # Check for exit key (ESC)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    print("Exiting...")
                    break

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Cleanup resources."""
        print("Cleaning up...")

        self.is_running = False

        # Release OS controls
        self.os_controller.release_all()

        # Release camera
        if self.camera:
            self.camera.release()

        # Close windows
        cv2.destroyAllWindows()

        # Close hand detector
        self.hand_detector.close()

        print("Cleanup complete")


def main():
    """Main entry point."""
    # Parse command line arguments
    config = Config()

    # Check for config file argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        try:
            config.load_from_file(config_file)
            print(f"Loaded configuration from: {config_file}")
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

    # Create and run controller
    controller = GestureController(config)
    controller.run()


if __name__ == "__main__":
    main()
