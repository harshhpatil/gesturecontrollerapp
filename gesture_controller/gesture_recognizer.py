"""Gesture recognition module."""

from collections import deque
from typing import Any, Optional

import numpy as np

from .config import Config


class GestureRecognizer:
    """Recognize gestures from hand landmarks."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize gesture recognizer.

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

        # Gesture buffer for stabilization
        self.gesture_buffer = deque(maxlen=self.config.GESTURE_BUFFER_SIZE)

        # Motion tracking for swipes and patterns
        self.position_history = deque(maxlen=self.config.SWIPE_BUFFER_SIZE)

        # Current stable gesture
        self.current_gesture = None

        # Two-handed gesture tracking
        self.two_hands_buffer = deque(maxlen=self.config.TWO_HANDS_CONFIDENCE_FRAMES)

    def recognize_gesture(
        self, finger_states: dict, hand_landmarks: Any, hand_detector: Any = None
    ) -> str:
        """Recognize gesture from finger states and landmarks.

        Args:
            finger_states: Dictionary of finger extended states
            hand_landmarks: Hand landmarks object
            hand_detector: HandDetector instance for distance calculations

        Returns:
            Recognized gesture name
        """
        if not finger_states:
            return "IDLE"

        # Validate finger states
        if not self._validate_finger_states(finger_states):
            return "IDLE"

        # Count extended fingers
        extended_count = sum(finger_states.values())

        # Pinch gesture (thumb and index close together)
        if hand_detector and hand_landmarks:
            try:
                thumb_index_dist = hand_detector.calculate_distance(hand_landmarks, 4, 8)
                if thumb_index_dist and thumb_index_dist < self.config.PINCH_THRESHOLD:
                    # Left click pinch (only thumb and index extended)
                    if finger_states["thumb"] and finger_states["index"] and extended_count == 2:
                        return "LEFT_CLICK"
                    # Drag pinch (index and middle)
                    if finger_states["index"] and finger_states["middle"] and extended_count == 2:
                        return "DRAG"
                    # Scroll pinch (thumb and index)
                    if finger_states["thumb"] and finger_states["index"]:
                        return "SCROLL"
            except (AttributeError, IndexError, TypeError) as e:
                if self.config.DEBUG_MODE:
                    print(f"Error in pinch detection: {e}")
                return "IDLE"

        # Palm gesture (all or most fingers extended) - Right click
        if extended_count >= self.config.PALM_THRESHOLD:
            if finger_states["index"] and finger_states["middle"] and finger_states["ring"]:
                return "RIGHT_CLICK"

        # Fist gesture (all fingers closed)
        if extended_count == 0:
            return "FIST"

        # Peace/Victory gesture (index and middle only)
        if (
            finger_states["index"]
            and finger_states["middle"]
            and not finger_states["ring"]
            and not finger_states["pinky"]
        ):
            return "VICTORY"

        # Three fingers (scroll mode)
        if (
            finger_states["index"]
            and finger_states["middle"]
            and finger_states["ring"]
            and not finger_states["pinky"]
        ):
            return "THREE_FINGERS"

        # Point gesture (index finger only)
        if (
            finger_states["index"]
            and not finger_states["middle"]
            and not finger_states["ring"]
            and not finger_states["pinky"]
        ):
            return "POINT"

        # Thumbs up
        if finger_states["thumb"] and not finger_states["index"] and not finger_states["middle"]:
            return "THUMBS_UP"

        return "IDLE"

    def stabilize_gesture(self, gesture: str) -> Optional[str]:
        """Stabilize gesture recognition using a buffer.

        Args:
            gesture: Current detected gesture

        Returns:
            Stable gesture or None if not confident
        """
        # Add to buffer
        self.gesture_buffer.append(gesture)

        # Count occurrences
        if len(self.gesture_buffer) < self.config.GESTURE_BUFFER_SIZE:
            return self.current_gesture

        # Find most common gesture
        gesture_counts = {}
        for g in self.gesture_buffer:
            gesture_counts[g] = gesture_counts.get(g, 0) + 1

        # Get gesture with highest count
        max_gesture = max(gesture_counts, key=gesture_counts.get)
        max_count = gesture_counts[max_gesture]

        # Only update if confidence threshold is met
        if max_count >= self.config.GESTURE_CONFIDENCE_THRESHOLD:
            self.current_gesture = max_gesture
            return max_gesture

        return self.current_gesture

    def detect_swipe(self, hand_landmarks: Any, hand_detector: Any) -> Optional[str]:
        """Detect swipe gestures.

        Args:
            hand_landmarks: Hand landmarks object
            hand_detector: HandDetector instance

        Returns:
            Swipe direction ("LEFT", "RIGHT", "UP", "DOWN") or None
        """
        if not hand_landmarks or not hand_detector:
            return None

        # Get index finger tip position
        index_tip = hand_detector.get_normalized_landmark(hand_landmarks, 8)
        if not index_tip:
            return None

        # Add to position history
        self.position_history.append(index_tip)

        # Need enough history
        if len(self.position_history) < self.config.SWIPE_BUFFER_SIZE:
            return None

        # Calculate movement from start to end
        start_pos = self.position_history[0]
        end_pos = self.position_history[-1]

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]

        # Calculate total distance
        distance = np.sqrt(dx**2 + dy**2)

        # Check if movement is significant
        if distance < self.config.SWIPE_THRESHOLD:
            return None

        # Determine dominant direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                return "RIGHT"
            else:
                return "LEFT"
        else:
            # Vertical swipe
            if dy > 0:
                return "DOWN"
            else:
                return "UP"

    def detect_circular_motion(self, hand_landmarks: Any, hand_detector: Any) -> Optional[str]:
        """Detect circular motion patterns.

        Args:
            hand_landmarks: Hand landmarks object
            hand_detector: HandDetector instance

        Returns:
            "CLOCKWISE" or "COUNTERCLOCKWISE" or None
        """
        if not hand_landmarks or not hand_detector:
            return None

        # Get index finger tip position
        index_tip = hand_detector.get_normalized_landmark(hand_landmarks, 8)
        if not index_tip:
            return None

        # Add to position history
        self.position_history.append(index_tip)

        # Need full buffer
        if len(self.position_history) < self.config.SWIPE_BUFFER_SIZE:
            return None

        # Calculate angles between consecutive points
        angles = []
        for i in range(1, len(self.position_history)):
            p1 = self.position_history[i - 1]
            p2 = self.position_history[i]

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            angle = np.arctan2(dy, dx)
            angles.append(angle)

        # Calculate total rotation
        total_rotation = 0
        for i in range(1, len(angles)):
            angle_diff = angles[i] - angles[i - 1]
            # Normalize to [-pi, pi]
            if angle_diff > np.pi:
                angle_diff -= 2 * np.pi
            elif angle_diff < -np.pi:
                angle_diff += 2 * np.pi
            total_rotation += angle_diff

        # Check if rotation is significant (more than 180 degrees)
        if abs(total_rotation) > np.pi:
            if total_rotation > 0:
                return "COUNTERCLOCKWISE"
            else:
                return "CLOCKWISE"

        return None

    def reset(self) -> None:
        """Reset gesture recognition state."""
        self.gesture_buffer.clear()
        self.position_history.clear()
        self.current_gesture = None
        self.two_hands_buffer.clear()

    def _validate_finger_states(self, finger_states: dict) -> bool:
        """Validate finger states dictionary.

        Args:
            finger_states: Dictionary of finger extended states

        Returns:
            True if valid, False otherwise
        """
        required_keys = {"thumb", "index", "middle", "ring", "pinky"}
        if not isinstance(finger_states, dict):
            return False
        return required_keys.issubset(finger_states.keys())

    def _validate_hand_landmarks(self, hand_landmarks: Any) -> bool:
        """Validate hand landmarks object.

        Args:
            hand_landmarks: Hand landmarks object to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not hand_landmarks or not hasattr(hand_landmarks, "landmark"):
                return False
            # Check if we have all 21 landmarks
            return len(hand_landmarks.landmark) == 21
        except (AttributeError, TypeError):
            return False

    def recognize_two_handed_gesture(
        self, hand_landmarks_list: list, hand_detector: Any
    ) -> Optional[str]:
        """Recognize two-handed gestures.

        Args:
            hand_landmarks_list: List of hand landmarks (should have 2 hands)
            hand_detector: HandDetector instance

        Returns:
            Two-handed gesture name or None
        """
        if not hand_landmarks_list or len(hand_landmarks_list) < 2:
            self.two_hands_buffer.clear()
            return None

        if not hand_detector:
            return None

        # Validate both hands
        hand1 = hand_landmarks_list[0]
        hand2 = hand_landmarks_list[1]

        if not self._validate_hand_landmarks(hand1) or not self._validate_hand_landmarks(hand2):
            self.two_hands_buffer.clear()
            return None

        try:
            # Get finger states for both hands
            finger_states1 = hand_detector.get_finger_states(hand1)
            finger_states2 = hand_detector.get_finger_states(hand2)

            # Validate finger states
            if not self._validate_finger_states(finger_states1) or not self._validate_finger_states(
                finger_states2
            ):
                self.two_hands_buffer.clear()
                return None

            # Count extended fingers for both hands
            extended1 = sum(finger_states1.values())
            extended2 = sum(finger_states2.values())

            # Two hands open gesture (both hands with open palms)
            min_fingers = self.config.TWO_HANDS_MIN_FINGERS
            if extended1 >= min_fingers and extended2 >= min_fingers:
                # Both hands have multiple fingers extended (open palm gesture)
                gesture_detected = True
            else:
                gesture_detected = False

            # Add to buffer for stabilization
            self.two_hands_buffer.append(gesture_detected)

            # Check if we have enough confidence
            if len(self.two_hands_buffer) >= self.config.TWO_HANDS_CONFIDENCE_FRAMES:
                # Count true values in buffer
                true_count = sum(self.two_hands_buffer)
                if true_count >= self.config.TWO_HANDS_CONFIDENCE_FRAMES:
                    return "TWO_HANDS_OPEN"

            return None

        except (AttributeError, IndexError, TypeError, KeyError) as e:
            if self.config.DEBUG_MODE:
                print(f"Error in two-handed gesture detection: {e}")
            self.two_hands_buffer.clear()
            return None
