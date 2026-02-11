"""Map gestures to OS-level actions."""

from typing import Any, Callable, Dict, Optional

from .config import Config


class ControlMapper:
    """Map recognized gestures to OS control actions."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize control mapper.

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

        # Default gesture-to-action mappings
        self.gesture_map = {
            "POINT": "move_cursor",
            "LEFT_CLICK": "left_click",
            "RIGHT_CLICK": "right_click",
            "DRAG": "drag",
            "SCROLL": "scroll",
            "THREE_FINGERS": "scroll",
            "VICTORY": "double_click",
            "THUMBS_UP": "pause",
            "FIST": "drag",
        }

        # Swipe-to-action mappings
        self.swipe_map = {
            "LEFT": "navigate_back",
            "RIGHT": "navigate_forward",
            "UP": "volume_up",
            "DOWN": "volume_down",
        }

        # Keyboard gesture mappings
        self.keyboard_map = {
            "PEACE": "copy",  # Peace sign for copy
            "OK": "paste",  # OK sign for paste
        }

        # Custom action handlers
        self.action_handlers: Dict[str, Callable] = {}

    def map_gesture_to_action(self, gesture: str) -> Optional[str]:
        """Map a gesture to its corresponding action.

        Args:
            gesture: Recognized gesture name

        Returns:
            Action name or None
        """
        return self.gesture_map.get(gesture)

    def map_swipe_to_action(self, swipe_direction: str) -> Optional[str]:
        """Map a swipe direction to its corresponding action.

        Args:
            swipe_direction: Swipe direction (LEFT, RIGHT, UP, DOWN)

        Returns:
            Action name or None
        """
        return self.swipe_map.get(swipe_direction)

    def map_keyboard_gesture(self, gesture: str) -> Optional[str]:
        """Map a gesture to keyboard action.

        Args:
            gesture: Gesture name

        Returns:
            Keyboard action name or None
        """
        return self.keyboard_map.get(gesture)

    def register_custom_mapping(self, gesture: str, action: str) -> None:
        """Register a custom gesture-to-action mapping.

        Args:
            gesture: Gesture name
            action: Action name
        """
        self.gesture_map[gesture] = action

    def register_action_handler(self, action: str, handler: Callable[[Any], None]) -> None:
        """Register a custom action handler.

        Args:
            action: Action name
            handler: Callable that handles the action
        """
        self.action_handlers[action] = handler

    def execute_action(self, action: str, *args, **kwargs) -> bool:
        """Execute a custom action if handler is registered.

        Args:
            action: Action name
            *args: Positional arguments for handler
            **kwargs: Keyword arguments for handler

        Returns:
            True if action was executed, False otherwise
        """
        if action in self.action_handlers:
            self.action_handlers[action](*args, **kwargs)
            return True
        return False

    def get_gesture_description(self, gesture: str) -> str:
        """Get human-readable description of a gesture.

        Args:
            gesture: Gesture name

        Returns:
            Description string
        """
        descriptions = {
            "POINT": "Point with index finger to move cursor",
            "LEFT_CLICK": "Pinch thumb and index to left click",
            "RIGHT_CLICK": "Open palm to right click",
            "DRAG": "Make fist or pinch index+middle to drag",
            "SCROLL": "Two-finger pinch with vertical motion to scroll",
            "THREE_FINGERS": "Show three fingers to scroll",
            "VICTORY": "Victory sign to double click",
            "THUMBS_UP": "Thumbs up to pause/resume",
            "FIST": "Closed fist to start dragging",
            "IDLE": "No active gesture",
        }
        return descriptions.get(gesture, "Unknown gesture")

    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current gesture-to-action mappings.

        Returns:
            Dictionary of gesture-to-action mappings
        """
        return {
            **self.gesture_map,
            **{f"swipe_{k}": v for k, v in self.swipe_map.items()},
            **{f"keyboard_{k}": v for k, v in self.keyboard_map.items()},
        }

    def load_mappings_from_dict(self, mappings: Dict[str, str]) -> None:
        """Load gesture mappings from a dictionary.

        Args:
            mappings: Dictionary of gesture-to-action mappings
        """
        for gesture, action in mappings.items():
            if gesture.startswith("swipe_"):
                direction = gesture.replace("swipe_", "")
                self.swipe_map[direction] = action
            elif gesture.startswith("keyboard_"):
                key = gesture.replace("keyboard_", "")
                self.keyboard_map[key] = action
            else:
                self.gesture_map[gesture] = action

    def reset_to_defaults(self) -> None:
        """Reset all mappings to default values."""
        self.__init__(self.config)
