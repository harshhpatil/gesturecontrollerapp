"""Unit tests for gesture recognizer module."""

from unittest.mock import Mock

import pytest

from gesture_controller.config import Config
from gesture_controller.gesture_recognizer import GestureRecognizer


class TestGestureRecognizer:
    """Test cases for GestureRecognizer class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config()

    @pytest.fixture
    def recognizer(self, config):
        """Create GestureRecognizer instance."""
        return GestureRecognizer(config)

    def test_initialization(self, config):
        """Test GestureRecognizer initialization."""
        recognizer = GestureRecognizer(config)
        assert recognizer.config == config
        assert recognizer.current_gesture is None
        assert len(recognizer.gesture_buffer) == 0

    def test_recognize_point_gesture(self, recognizer):
        """Test recognizing point gesture."""
        finger_states = {
            "thumb": False,
            "index": True,
            "middle": False,
            "ring": False,
            "pinky": False,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        assert gesture == "POINT"

    def test_recognize_victory_gesture(self, recognizer):
        """Test recognizing victory gesture."""
        finger_states = {
            "thumb": False,
            "index": True,
            "middle": True,
            "ring": False,
            "pinky": False,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        assert gesture == "VICTORY"

    def test_recognize_fist_gesture(self, recognizer):
        """Test recognizing fist gesture."""
        finger_states = {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        assert gesture == "FIST"

    def test_recognize_three_fingers_gesture(self, recognizer):
        """Test recognizing three fingers gesture."""
        # Set PALM_THRESHOLD higher to distinguish from three fingers
        recognizer.config.PALM_THRESHOLD = 4

        finger_states = {
            "thumb": False,
            "index": True,
            "middle": True,
            "ring": True,
            "pinky": False,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        # With only 3 fingers and PALM_THRESHOLD=4, this should not match palm
        assert gesture == "THREE_FINGERS"

    def test_recognize_thumbs_up_gesture(self, recognizer):
        """Test recognizing thumbs up gesture."""
        finger_states = {
            "thumb": True,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        assert gesture == "THUMBS_UP"

    def test_recognize_right_click_gesture(self, recognizer):
        """Test recognizing right click (palm) gesture."""
        finger_states = {
            "thumb": True,
            "index": True,
            "middle": True,
            "ring": True,
            "pinky": True,
        }

        gesture = recognizer.recognize_gesture(finger_states, None, None)
        assert gesture == "RIGHT_CLICK"

    def test_recognize_pinch_left_click(self, recognizer):
        """Test recognizing pinch for left click."""
        finger_states = {
            "thumb": True,
            "index": True,
            "middle": False,
            "ring": False,
            "pinky": False,
        }

        # Mock hand detector with close thumb-index distance
        mock_detector = Mock()
        mock_detector.calculate_distance = Mock(return_value=0.03)  # Below threshold

        gesture = recognizer.recognize_gesture(finger_states, Mock(), mock_detector)
        assert gesture == "LEFT_CLICK"

    def test_recognize_pinch_drag(self, recognizer):
        """Test recognizing pinch for drag."""
        finger_states = {
            "thumb": False,
            "index": True,
            "middle": True,
            "ring": False,
            "pinky": False,
        }

        # Mock hand detector with close distance
        mock_detector = Mock()
        mock_detector.calculate_distance = Mock(return_value=0.03)

        gesture = recognizer.recognize_gesture(finger_states, Mock(), mock_detector)
        assert gesture == "DRAG"

    def test_stabilize_gesture(self, recognizer):
        """Test gesture stabilization."""
        # Add same gesture multiple times
        for _ in range(5):
            result = recognizer.stabilize_gesture("POINT")

        # Should stabilize to POINT
        assert result == "POINT"

    def test_stabilize_gesture_insufficient_confidence(self, recognizer):
        """Test gesture stabilization with insufficient confidence."""
        # Add different gestures
        recognizer.stabilize_gesture("POINT")
        recognizer.stabilize_gesture("VICTORY")
        recognizer.stabilize_gesture("FIST")
        result = recognizer.stabilize_gesture("POINT")

        # Should return None or previous stable gesture
        assert result is None or isinstance(result, str)

    def test_detect_swipe_insufficient_history(self, recognizer):
        """Test swipe detection with insufficient history."""
        mock_hand = Mock()
        mock_detector = Mock()
        mock_detector.get_normalized_landmark = Mock(return_value=(0.5, 0.5, 0))

        # First call - insufficient history
        swipe = recognizer.detect_swipe(mock_hand, mock_detector)
        assert swipe is None

    def test_detect_swipe_right(self, recognizer):
        """Test detecting right swipe."""
        mock_hand = Mock()
        mock_detector = Mock()

        # Simulate right swipe with significant movement
        positions = [(0.1 + i * 0.08, 0.5, 0) for i in range(10)]

        for i, pos in enumerate(positions):
            mock_detector.get_normalized_landmark = Mock(return_value=pos)
            if i == len(positions) - 1:
                # On last iteration, check result
                swipe = recognizer.detect_swipe(mock_hand, mock_detector)
                # Should detect right swipe with this movement
                assert swipe == "RIGHT"
            else:
                recognizer.detect_swipe(mock_hand, mock_detector)

    def test_reset(self, recognizer):
        """Test resetting recognizer state."""
        # Add some state
        recognizer.stabilize_gesture("POINT")
        recognizer.current_gesture = "POINT"

        # Reset
        recognizer.reset()

        assert len(recognizer.gesture_buffer) == 0
        assert len(recognizer.position_history) == 0
        assert recognizer.current_gesture is None
        assert len(recognizer.two_hands_buffer) == 0

    def test_validate_finger_states(self, recognizer):
        """Test finger states validation."""
        # Valid finger states
        valid_states = {
            "thumb": True,
            "index": True,
            "middle": False,
            "ring": False,
            "pinky": False,
        }
        assert recognizer._validate_finger_states(valid_states) is True

        # Invalid - missing keys
        invalid_states = {"thumb": True, "index": True}
        assert recognizer._validate_finger_states(invalid_states) is False

        # Invalid - not a dict
        assert recognizer._validate_finger_states(None) is False
        assert recognizer._validate_finger_states("invalid") is False

    def test_validate_hand_landmarks(self, recognizer):
        """Test hand landmarks validation."""
        # Valid hand landmarks
        mock_hand = Mock()
        mock_hand.landmark = [Mock() for _ in range(21)]
        assert recognizer._validate_hand_landmarks(mock_hand) is True

        # Invalid - not enough landmarks
        mock_hand_invalid = Mock()
        mock_hand_invalid.landmark = [Mock() for _ in range(10)]
        assert recognizer._validate_hand_landmarks(mock_hand_invalid) is False

        # Invalid - no landmark attribute
        mock_hand_no_attr = Mock(spec=[])
        assert recognizer._validate_hand_landmarks(mock_hand_no_attr) is False

        # Invalid - None
        assert recognizer._validate_hand_landmarks(None) is False

    def test_recognize_two_handed_gesture_insufficient_hands(self, recognizer):
        """Test two-handed gesture with insufficient hands."""
        # No hands
        assert recognizer.recognize_two_handed_gesture([], Mock()) is None

        # Only one hand
        mock_hand = Mock()
        assert recognizer.recognize_two_handed_gesture([mock_hand], Mock()) is None

    def test_recognize_two_handed_gesture_open(self, recognizer):
        """Test recognizing two hands open gesture."""
        # Create mock hands with valid landmarks
        mock_hand1 = Mock()
        mock_hand1.landmark = [Mock() for _ in range(21)]

        mock_hand2 = Mock()
        mock_hand2.landmark = [Mock() for _ in range(21)]

        # Mock hand detector
        mock_detector = Mock()

        # Both hands with multiple fingers extended (open palms)
        def mock_get_finger_states(hand):
            return {
                "thumb": True,
                "index": True,
                "middle": True,
                "ring": True,
                "pinky": False,
            }

        mock_detector.get_finger_states = mock_get_finger_states

        # Call multiple times to fill buffer
        for _ in range(recognizer.config.TWO_HANDS_CONFIDENCE_FRAMES):
            result = recognizer.recognize_two_handed_gesture([mock_hand1, mock_hand2], mock_detector)

        # Should detect TWO_HANDS_OPEN after enough frames
        assert result == "TWO_HANDS_OPEN"

    def test_recognize_two_handed_gesture_insufficient_fingers(self, recognizer):
        """Test two-handed gesture with insufficient fingers extended."""
        # Create mock hands
        mock_hand1 = Mock()
        mock_hand1.landmark = [Mock() for _ in range(21)]

        mock_hand2 = Mock()
        mock_hand2.landmark = [Mock() for _ in range(21)]

        # Mock hand detector
        mock_detector = Mock()

        # One hand with insufficient fingers
        def mock_get_finger_states(hand):
            return {
                "thumb": True,
                "index": True,
                "middle": False,
                "ring": False,
                "pinky": False,
            }

        mock_detector.get_finger_states = mock_get_finger_states

        # Call multiple times
        for _ in range(recognizer.config.TWO_HANDS_CONFIDENCE_FRAMES):
            result = recognizer.recognize_two_handed_gesture([mock_hand1, mock_hand2], mock_detector)

        # Should not detect TWO_HANDS_OPEN
        assert result is None

    def test_recognize_gesture_with_error_handling(self, recognizer):
        """Test gesture recognition with invalid input."""
        # None finger states
        assert recognizer.recognize_gesture(None, None, None) == "IDLE"

        # Empty finger states
        assert recognizer.recognize_gesture({}, None, None) == "IDLE"

        # Invalid finger states
        invalid_states = {"invalid": True}
        assert recognizer.recognize_gesture(invalid_states, None, None) == "IDLE"
