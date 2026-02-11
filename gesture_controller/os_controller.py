"""OS-level control execution module using pynput."""

import time
from typing import Optional, Tuple

import pyautogui
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController

from .config import Config


class OSController:
    """Execute OS-level mouse and keyboard actions."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize OS controller.

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

        # Initialize pynput controllers
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()

        # State tracking
        self.is_dragging = False
        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.last_double_click_time = 0

        # Cursor position smoothing
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2

        # Disable PyAutoGUI failsafe for smooth operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    def move_cursor(self, normalized_x: float, normalized_y: float, smooth: bool = True) -> None:
        """Move cursor to normalized position.

        Args:
            normalized_x: X position (0.0-1.0)
            normalized_y: Y position (0.0-1.0)
            smooth: Apply smoothing to movement
        """
        # Convert to screen coordinates (flip X for mirror effect)
        target_x = int((1 - normalized_x) * self.screen_width)
        target_y = int(normalized_y * self.screen_height)

        # Apply speed multiplier
        target_x = int(target_x * self.config.MOUSE_SPEED_MULTIPLIER)
        target_y = int(target_y * self.config.MOUSE_SPEED_MULTIPLIER)

        # Clamp to screen bounds
        target_x = max(0, min(target_x, self.screen_width - 1))
        target_y = max(0, min(target_y, self.screen_height - 1))

        if smooth:
            # Apply exponential smoothing
            self.current_x += (target_x - self.current_x) * self.config.CURSOR_SMOOTHING
            self.current_y += (target_y - self.current_y) * self.config.CURSOR_SMOOTHING

            x = int(self.current_x)
            y = int(self.current_y)
        else:
            x = target_x
            y = target_y
            self.current_x = x
            self.current_y = y

        # Move cursor
        try:
            self.mouse.position = (x, y)
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Cursor move error: {e}")

    def left_click(self) -> None:
        """Perform left mouse click with cooldown."""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_left_click_time < self.config.LEFT_CLICK_COOLDOWN:
            return

        try:
            self.mouse.click(Button.left, 1)
            self.last_left_click_time = current_time
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Left click error: {e}")

    def right_click(self) -> None:
        """Perform right mouse click with cooldown."""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_right_click_time < self.config.RIGHT_CLICK_COOLDOWN:
            return

        try:
            self.mouse.click(Button.right, 1)
            self.last_right_click_time = current_time
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Right click error: {e}")

    def double_click(self) -> None:
        """Perform double click."""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_double_click_time < self.config.DOUBLE_CLICK_THRESHOLD * 2:
            return

        try:
            self.mouse.click(Button.left, 2)
            self.last_double_click_time = current_time
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Double click error: {e}")

    def start_drag(self) -> None:
        """Start dragging operation."""
        if not self.is_dragging:
            try:
                self.mouse.press(Button.left)
                self.is_dragging = True
            except Exception as e:
                if self.config.DEBUG_MODE:
                    print(f"Drag start error: {e}")

    def stop_drag(self) -> None:
        """Stop dragging operation."""
        if self.is_dragging:
            try:
                self.mouse.release(Button.left)
                self.is_dragging = False
            except Exception as e:
                if self.config.DEBUG_MODE:
                    print(f"Drag stop error: {e}")

    def scroll(self, amount: int) -> None:
        """Scroll vertically.

        Args:
            amount: Scroll amount (positive = down, negative = up)
        """
        # Apply scroll multiplier
        scroll_amount = int(amount * self.config.SCROLL_MULTIPLIER)

        # Clamp to max
        scroll_amount = max(
            -self.config.SCROLL_MAX_AMOUNT, min(scroll_amount, self.config.SCROLL_MAX_AMOUNT)
        )

        try:
            # pynput scroll (positive = up, negative = down)
            self.mouse.scroll(0, -scroll_amount // 10)
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Scroll error: {e}")

    def type_text(self, text: str) -> None:
        """Type text using keyboard.

        Args:
            text: Text to type
        """
        if not self.config.KEYBOARD_ENABLED:
            return

        try:
            for char in text:
                self.keyboard.press(char)
                self.keyboard.release(char)
                time.sleep(0.01)  # Small delay between keystrokes
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Type text error: {e}")

    def press_key(self, key: str) -> None:
        """Press a single key.

        Args:
            key: Key to press (use Key enum for special keys)
        """
        if not self.config.KEYBOARD_ENABLED:
            return

        try:
            # Check if it's a special key
            if hasattr(Key, key):
                key_obj = getattr(Key, key)
                self.keyboard.press(key_obj)
                self.keyboard.release(key_obj)
            else:
                self.keyboard.press(key)
                self.keyboard.release(key)
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Press key error: {e}")

    def press_hotkey(self, *keys: str) -> None:
        """Press a hotkey combination.

        Args:
            *keys: Keys to press simultaneously
        """
        if not self.config.KEYBOARD_ENABLED:
            return

        try:
            # Press all keys
            key_objects = []
            for key in keys:
                if hasattr(Key, key):
                    key_obj = getattr(Key, key)
                else:
                    key_obj = key
                key_objects.append(key_obj)
                self.keyboard.press(key_obj)

            # Release in reverse order
            for key_obj in reversed(key_objects):
                self.keyboard.release(key_obj)
        except Exception as e:
            if self.config.DEBUG_MODE:
                print(f"Hotkey error: {e}")

    def copy(self) -> None:
        """Execute copy command (Ctrl+C)."""
        self.press_hotkey("ctrl", "c")

    def paste(self) -> None:
        """Execute paste command (Ctrl+V)."""
        self.press_hotkey("ctrl", "v")

    def undo(self) -> None:
        """Execute undo command (Ctrl+Z)."""
        self.press_hotkey("ctrl", "z")

    def redo(self) -> None:
        """Execute redo command (Ctrl+Y)."""
        self.press_hotkey("ctrl", "y")

    def navigate_back(self) -> None:
        """Navigate back (Alt+Left)."""
        self.press_hotkey("alt", "left")

    def navigate_forward(self) -> None:
        """Navigate forward (Alt+Right)."""
        self.press_hotkey("alt", "right")

    def volume_up(self) -> None:
        """Increase volume."""
        pyautogui.press("volumeup")

    def volume_down(self) -> None:
        """Decrease volume."""
        pyautogui.press("volumedown")

    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return self.mouse.position

    def release_all(self) -> None:
        """Release all pressed buttons and keys."""
        self.stop_drag()
