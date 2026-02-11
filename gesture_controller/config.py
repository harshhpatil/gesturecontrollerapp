"""Configuration management for gesture controller."""

import os
from typing import Any, Dict


class Config:
    """Configuration manager for gesture controller settings."""

    # Camera settings
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480

    # Hand detection settings (MediaPipe)
    MAX_NUM_HANDS: int = 2  # Support two hands for two-handed gestures
    MODEL_COMPLEXITY: int = 0  # 0 or 1 (0 is faster)
    MIN_DETECTION_CONFIDENCE: float = 0.6
    MIN_TRACKING_CONFIDENCE: float = 0.6

    # Mouse control settings
    CURSOR_SMOOTHING: float = 0.6  # 0.0-1.0, higher = faster
    MOUSE_SPEED_MULTIPLIER: float = 1.0

    # Gesture detection settings
    PINCH_THRESHOLD: float = 0.05  # Distance for pinch detection
    PALM_THRESHOLD: int = 3  # Minimum fingers for palm gesture
    GESTURE_BUFFER_SIZE: int = 5  # Frames to buffer for stability
    GESTURE_CONFIDENCE_THRESHOLD: int = 3  # Minimum occurrences to confirm

    # Two-handed gesture settings
    TWO_HANDS_MIN_FINGERS: int = 3  # Minimum fingers extended per hand for open palm
    TWO_HANDS_CONFIDENCE_FRAMES: int = 3  # Frames to confirm two-handed gesture

    # Click settings
    LEFT_CLICK_COOLDOWN: float = 0.5  # Seconds between left clicks
    RIGHT_CLICK_COOLDOWN: float = 0.5  # Seconds between right clicks
    DOUBLE_CLICK_THRESHOLD: float = 0.3  # Max time between double clicks

    # Scroll settings
    SCROLL_MULTIPLIER: int = 30  # Pixels per scroll unit
    SCROLL_DEADZONE: float = 0.015  # Ignore small movements
    SCROLL_MAX_AMOUNT: int = 50  # Maximum scroll per frame

    # Drag settings
    DRAG_HOLD_TIME: float = 0.3  # Seconds to hold before dragging starts
    DRAG_THRESHOLD: float = 0.05  # Distance threshold for drag detection

    # Keyboard settings
    KEYBOARD_ENABLED: bool = True
    KEYBOARD_HOLD_TIME: float = 0.5  # Seconds to hold gesture for key press

    # Swipe settings
    SWIPE_THRESHOLD: float = 0.15  # Minimum distance for swipe
    SWIPE_BUFFER_SIZE: int = 10  # Frames to track
    SWIPE_VELOCITY_THRESHOLD: float = 0.02  # Minimum velocity

    # Display settings
    SHOW_FPS: bool = True
    SHOW_LANDMARKS: bool = True
    SHOW_GESTURES: bool = True
    FRAME_SKIP: int = 1  # Display every Nth frame (1 = all frames)
    WINDOW_NAME: str = "Gesture Controller"

    # Performance settings
    PROCESSING_THREAD_ENABLED: bool = True
    MAX_PROCESSING_FPS: int = 30

    # Pause settings
    PAUSE_COOLDOWN: float = 1.0  # Seconds between pause toggles
    HARSH_PAUSE_ENABLED: bool = True  # Enable two-handed harsh pause

    # Debug settings
    DEBUG_MODE: bool = os.getenv("DEBUG", "false").lower() == "true"
    VERBOSE: bool = False

    @classmethod
    def load_from_dict(cls, config_dict: Dict[str, Any]) -> None:
        """Load configuration from dictionary.

        Args:
            config_dict: Dictionary containing configuration values
        """
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)

    @classmethod
    def load_from_file(cls, filepath: str) -> None:
        """Load configuration from JSON or YAML file.

        Args:
            filepath: Path to configuration file
        """
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.endswith(".json"):
                config_dict = json.load(f)
                cls.load_from_dict(config_dict)
            else:
                raise ValueError(f"Unsupported file format: {filepath}")

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary.

        Returns:
            Dictionary containing all configuration values
        """
        return {
            key: value
            for key, value in vars(cls).items()
            if not key.startswith("_") and key.isupper()
        }
