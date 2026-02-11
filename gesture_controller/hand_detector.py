"""Hand detection module using MediaPipe."""

from typing import List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from .config import Config


class HandDetector:
    """Detect and track hand landmarks using MediaPipe."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize hand detector.

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.MAX_NUM_HANDS,
            model_complexity=self.config.MODEL_COMPLEXITY,
            min_detection_confidence=self.config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.MIN_TRACKING_CONFIDENCE,
        )

        self.results = None
        self.frame_width = 0
        self.frame_height = 0

    def detect_hands(self, frame: np.ndarray) -> Tuple[bool, Optional[List]]:
        """Detect hands in the given frame.

        Args:
            frame: BGR image from webcam

        Returns:
            Tuple of (hands_found, hand_landmarks_list)
        """
        # Store frame dimensions
        self.frame_height, self.frame_width = frame.shape[:2]

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        self.results = self.hands.process(rgb_frame)

        # Return detection results
        if self.results.multi_hand_landmarks:
            return True, self.results.multi_hand_landmarks
        return False, None

    def get_hand_landmarks(self, hand_index: int = 0) -> Optional[List]:
        """Get landmarks for a specific hand.

        Args:
            hand_index: Index of the hand (0 for first hand)

        Returns:
            Hand landmarks or None if not found
        """
        if (
            self.results
            and self.results.multi_hand_landmarks
            and len(self.results.multi_hand_landmarks) > hand_index
        ):
            return self.results.multi_hand_landmarks[hand_index]
        return None

    def get_landmark_position(self, hand_landmarks, landmark_id: int) -> Optional[Tuple[int, int]]:
        """Get pixel coordinates of a specific landmark.

        Args:
            hand_landmarks: Hand landmarks object
            landmark_id: ID of the landmark (0-20)

        Returns:
            Tuple of (x, y) pixel coordinates or None
        """
        if hand_landmarks and 0 <= landmark_id < 21:
            landmark = hand_landmarks.landmark[landmark_id]
            x = int(landmark.x * self.frame_width)
            y = int(landmark.y * self.frame_height)
            return (x, y)
        return None

    def get_normalized_landmark(
        self, hand_landmarks, landmark_id: int
    ) -> Optional[Tuple[float, float, float]]:
        """Get normalized coordinates of a landmark.

        Args:
            hand_landmarks: Hand landmarks object
            landmark_id: ID of the landmark (0-20)

        Returns:
            Tuple of (x, y, z) normalized coordinates or None
        """
        if hand_landmarks and 0 <= landmark_id < 21:
            landmark = hand_landmarks.landmark[landmark_id]
            return (landmark.x, landmark.y, landmark.z)
        return None

    def calculate_distance(self, hand_landmarks, point1_id: int, point2_id: int) -> Optional[float]:
        """Calculate normalized distance between two landmarks.

        Args:
            hand_landmarks: Hand landmarks object
            point1_id: First landmark ID
            point2_id: Second landmark ID

        Returns:
            Normalized distance or None
        """
        p1 = self.get_normalized_landmark(hand_landmarks, point1_id)
        p2 = self.get_normalized_landmark(hand_landmarks, point2_id)

        if p1 and p2:
            return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return None

    def get_finger_states(self, hand_landmarks) -> dict:
        """Detect which fingers are extended.

        Args:
            hand_landmarks: Hand landmarks object

        Returns:
            Dictionary with finger states (True = extended)
        """
        if not hand_landmarks:
            return {
                "thumb": False,
                "index": False,
                "middle": False,
                "ring": False,
                "pinky": False,
            }

        landmarks = hand_landmarks.landmark

        # Thumb: check x-axis distance (assumes right hand or mirrored)
        thumb_extended = landmarks[4].x > landmarks[3].x

        # Other fingers: check y-axis (tip vs middle joint)
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky
        finger_mids = [6, 10, 14, 18]

        fingers_extended = []
        for tip, mid in zip(finger_tips, finger_mids):
            fingers_extended.append(landmarks[tip].y < landmarks[mid].y)

        return {
            "thumb": thumb_extended,
            "index": fingers_extended[0],
            "middle": fingers_extended[1],
            "ring": fingers_extended[2],
            "pinky": fingers_extended[3],
        }

    def draw_landmarks(self, frame: np.ndarray, hand_landmarks) -> None:
        """Draw hand landmarks on the frame.

        Args:
            frame: Image frame to draw on
            hand_landmarks: Hand landmarks to draw
        """
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style(),
            )

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self.hands:
            self.hands.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
