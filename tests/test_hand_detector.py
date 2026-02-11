"""Unit tests for hand detector module."""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from gesture_controller.hand_detector import HandDetector
from gesture_controller.config import Config


class TestHandDetector:
    """Test cases for HandDetector class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config()

    @pytest.fixture
    def detector(self, config):
        """Create HandDetector instance."""
        with patch('gesture_controller.hand_detector.mp'):
            detector = HandDetector(config)
            detector.mp_hands = Mock()
            detector.hands = Mock()
            return detector

    def test_initialization(self, config):
        """Test HandDetector initialization."""
        with patch('gesture_controller.hand_detector.mp'):
            detector = HandDetector(config)
            assert detector.config == config
            assert detector.results is None

    def test_detect_hands_no_hands(self, detector):
        """Test hand detection when no hands are present."""
        # Create mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock no hands detected
        detector.hands.process = Mock(return_value=Mock(multi_hand_landmarks=None))
        
        # Detect hands
        found, landmarks = detector.detect_hands(frame)
        
        assert found is False
        assert landmarks is None

    def test_detect_hands_with_hands(self, detector):
        """Test hand detection when hands are present."""
        # Create mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock hands detected
        mock_landmarks = [Mock()]
        detector.hands.process = Mock(
            return_value=Mock(multi_hand_landmarks=mock_landmarks)
        )
        
        # Detect hands
        found, landmarks = detector.detect_hands(frame)
        
        assert found is True
        assert landmarks == mock_landmarks

    def test_get_hand_landmarks(self, detector):
        """Test getting hand landmarks."""
        mock_landmarks = [Mock(), Mock()]
        detector.results = Mock(multi_hand_landmarks=mock_landmarks)
        
        # Get first hand
        landmarks = detector.get_hand_landmarks(0)
        assert landmarks == mock_landmarks[0]
        
        # Get second hand
        landmarks = detector.get_hand_landmarks(1)
        assert landmarks == mock_landmarks[1]
        
        # Invalid index
        landmarks = detector.get_hand_landmarks(2)
        assert landmarks is None

    def test_get_landmark_position(self, detector):
        """Test getting landmark pixel position."""
        detector.frame_width = 640
        detector.frame_height = 480
        
        # Create mock landmark
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        
        mock_hand = Mock()
        mock_hand.landmark = [mock_landmark] * 21
        
        # Get position
        pos = detector.get_landmark_position(mock_hand, 0)
        
        assert pos == (320, 240)

    def test_calculate_distance(self, detector):
        """Test calculating distance between landmarks."""
        # Create mock landmarks
        mock_landmarks = []
        for i in range(21):
            mock_landmark = Mock()
            mock_landmark.x = i * 0.1
            mock_landmark.y = i * 0.1
            mock_landmark.z = 0
            mock_landmarks.append(mock_landmark)
        
        mock_hand = Mock()
        mock_hand.landmark = mock_landmarks
        
        # Calculate distance
        dist = detector.calculate_distance(mock_hand, 0, 10)
        
        assert dist is not None
        assert dist > 0

    def test_get_finger_states(self, detector):
        """Test finger state detection."""
        # Create mock hand with all fingers extended
        mock_landmarks = []
        for i in range(21):
            mock_landmark = Mock()
            mock_landmark.x = 0.5
            mock_landmark.y = 0.5 - (i * 0.01)  # Fingers pointing up
            mock_landmarks.append(mock_landmark)
        
        # Adjust specific landmarks for finger detection
        mock_landmarks[4].x = 0.6  # Thumb extended
        mock_landmarks[8].y = 0.3  # Index tip above base
        mock_landmarks[12].y = 0.3  # Middle tip above base
        mock_landmarks[16].y = 0.3  # Ring tip above base
        mock_landmarks[20].y = 0.3  # Pinky tip above base
        
        mock_hand = Mock()
        mock_hand.landmark = mock_landmarks
        
        finger_states = detector.get_finger_states(mock_hand)
        
        assert isinstance(finger_states, dict)
        assert "thumb" in finger_states
        assert "index" in finger_states
        assert "middle" in finger_states
        assert "ring" in finger_states
        assert "pinky" in finger_states

    def test_close(self, detector):
        """Test closing detector."""
        detector.hands = Mock()
        detector.close()
        detector.hands.close.assert_called_once()
