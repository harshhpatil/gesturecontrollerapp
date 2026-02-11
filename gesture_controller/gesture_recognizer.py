"""Gesture recognition module."""

from collections import deque
from typing import Optional

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

    def recognize_gesture(self, finger_states: dict, hand_landmarks, hand_detector=None) -> str:
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

        # Count extended fingers
        extended_count = sum(finger_states.values())

        # Pinch gesture (thumb and index close together)
        if hand_detector and hand_landmarks:
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

    def detect_swipe(self, hand_landmarks, hand_detector) -> Optional[str]:
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

    def detect_circular_motion(self, hand_landmarks, hand_detector) -> Optional[str]:
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
