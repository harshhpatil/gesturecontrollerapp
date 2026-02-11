"""Unit tests for OS controller module."""

from unittest.mock import Mock, patch

import pytest

from gesture_controller.config import Config
from gesture_controller.os_controller import OSController


class TestOSController:
    """Test cases for OSController class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = Config()
        config.DEBUG_MODE = False  # Disable debug output in tests
        return config

    @pytest.fixture
    def controller(self, config):
        """Create OSController instance with mocked pynput."""
        with (
            patch("gesture_controller.os_controller.MouseController"),
            patch("gesture_controller.os_controller.KeyboardController"),
            patch("gesture_controller.os_controller.pyautogui") as mock_pyautogui,
        ):
            mock_pyautogui.size.return_value = (1920, 1080)

            from gesture_controller.os_controller import OSController

            controller = OSController(config)
            controller.mouse = Mock()
            controller.keyboard = Mock()
            return controller

    def test_initialization(self, config):
        """Test OSController initialization."""
        with (
            patch("gesture_controller.os_controller.MouseController"),
            patch("gesture_controller.os_controller.KeyboardController"),
            patch("gesture_controller.os_controller.pyautogui") as mock_pyautogui,
        ):
            mock_pyautogui.size.return_value = (1920, 1080)

            from gesture_controller.os_controller import OSController

            controller = OSController(config)
            assert controller.config == config
            assert controller.is_dragging is False

    def test_move_cursor(self, controller):
        """Test cursor movement."""
        controller.mouse.position = (0, 0)

        # Move to center
        controller.move_cursor(0.5, 0.5, smooth=False)

        # Check that position was set
        assert controller.mouse.position is not None

    def test_left_click(self, controller):
        """Test left click."""
        controller.left_click()

        # Should call mouse click
        controller.mouse.click.assert_called_once()

    def test_left_click_cooldown(self, controller):
        """Test left click cooldown."""
        controller.last_left_click_time = 0

        # First click
        controller.left_click()
        assert controller.mouse.click.call_count == 1

        # Immediate second click should be blocked by cooldown
        controller.left_click()
        assert controller.mouse.click.call_count == 1

    def test_right_click(self, controller):
        """Test right click."""
        controller.right_click()

        # Should call mouse click
        controller.mouse.click.assert_called_once()

    def test_double_click(self, controller):
        """Test double click."""
        controller.double_click()

        # Should call mouse click
        controller.mouse.click.assert_called_once()

    def test_start_drag(self, controller):
        """Test starting drag operation."""
        assert controller.is_dragging is False

        controller.start_drag()

        assert controller.is_dragging is True
        controller.mouse.press.assert_called_once()

    def test_stop_drag(self, controller):
        """Test stopping drag operation."""
        controller.is_dragging = True

        controller.stop_drag()

        assert controller.is_dragging is False
        controller.mouse.release.assert_called_once()

    def test_scroll(self, controller):
        """Test scrolling."""
        controller.scroll(5)

        # Should call mouse scroll
        controller.mouse.scroll.assert_called_once()

    def test_type_text(self, controller):
        """Test typing text."""
        controller.config.KEYBOARD_ENABLED = True

        controller.type_text("hello")

        # Should press and release each character
        assert controller.keyboard.press.call_count == 5
        assert controller.keyboard.release.call_count == 5

    def test_type_text_disabled(self, controller):
        """Test typing when keyboard is disabled."""
        controller.config.KEYBOARD_ENABLED = False

        controller.type_text("hello")

        # Should not call keyboard
        controller.keyboard.press.assert_not_called()

    def test_press_key(self, controller):
        """Test pressing a single key."""
        controller.config.KEYBOARD_ENABLED = True

        controller.press_key("a")

        controller.keyboard.press.assert_called_once()
        controller.keyboard.release.assert_called_once()

    def test_press_hotkey(self, controller):
        """Test pressing hotkey combination."""
        controller.config.KEYBOARD_ENABLED = True

        controller.press_hotkey("ctrl", "c")

        # Should press and release keys
        assert controller.keyboard.press.call_count >= 2
        assert controller.keyboard.release.call_count >= 2

    def test_copy(self, controller):
        """Test copy command."""
        controller.config.KEYBOARD_ENABLED = True

        controller.copy()

        # Should call keyboard methods
        assert controller.keyboard.press.called

    def test_paste(self, controller):
        """Test paste command."""
        controller.config.KEYBOARD_ENABLED = True

        controller.paste()

        # Should call keyboard methods
        assert controller.keyboard.press.called

    def test_navigate_back(self, controller):
        """Test navigate back."""
        controller.config.KEYBOARD_ENABLED = True

        controller.navigate_back()

        # Should call keyboard methods
        assert controller.keyboard.press.called

    def test_navigate_forward(self, controller):
        """Test navigate forward."""
        controller.config.KEYBOARD_ENABLED = True

        controller.navigate_forward()

        # Should call keyboard methods
        assert controller.keyboard.press.called

    def test_get_cursor_position(self, controller):
        """Test getting cursor position."""
        controller.mouse.position = (100, 200)

        pos = controller.get_cursor_position()

        assert pos == (100, 200)

    def test_release_all(self, controller):
        """Test releasing all controls."""
        controller.is_dragging = True

        controller.release_all()

        assert controller.is_dragging is False
        controller.mouse.release.assert_called_once()
