"""Pytest configuration for gesture controller tests."""

import sys
from unittest.mock import Mock, MagicMock

# Create proper mock for pyautogui
mock_pyautogui = MagicMock()
mock_pyautogui.size.return_value = (1920, 1080)
mock_pyautogui.FAILSAFE = False
mock_pyautogui.PAUSE = 0

# Create proper mocks for pynput
mock_pynput = MagicMock()
mock_pynput_mouse = MagicMock()
mock_pynput_keyboard = MagicMock()

# Mock modules before any imports
sys.modules["pyautogui"] = mock_pyautogui
sys.modules["pynput"] = mock_pynput
sys.modules["pynput.mouse"] = mock_pynput_mouse
sys.modules["pynput.keyboard"] = mock_pynput_keyboard
