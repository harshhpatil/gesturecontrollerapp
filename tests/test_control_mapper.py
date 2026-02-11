"""Unit tests for control mapper module."""

from unittest.mock import Mock

import pytest

from gesture_controller.config import Config
from gesture_controller.control_mapper import ControlMapper


class TestControlMapper:
    """Test cases for ControlMapper class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config()

    @pytest.fixture
    def mapper(self, config):
        """Create ControlMapper instance."""
        return ControlMapper(config)

    def test_initialization(self, config):
        """Test ControlMapper initialization."""
        mapper = ControlMapper(config)
        assert mapper.config == config
        assert isinstance(mapper.gesture_map, dict)
        assert isinstance(mapper.swipe_map, dict)

    def test_map_gesture_to_action(self, mapper):
        """Test mapping gesture to action."""
        # Test known mapping
        action = mapper.map_gesture_to_action("POINT")
        assert action == "move_cursor"

        action = mapper.map_gesture_to_action("LEFT_CLICK")
        assert action == "left_click"

        # Test unknown gesture
        action = mapper.map_gesture_to_action("UNKNOWN")
        assert action is None

    def test_map_swipe_to_action(self, mapper):
        """Test mapping swipe to action."""
        # Test known swipe
        action = mapper.map_swipe_to_action("LEFT")
        assert action == "navigate_back"

        action = mapper.map_swipe_to_action("RIGHT")
        assert action == "navigate_forward"

        # Test unknown swipe
        action = mapper.map_swipe_to_action("DIAGONAL")
        assert action is None

    def test_register_custom_mapping(self, mapper):
        """Test registering custom gesture mapping."""
        mapper.register_custom_mapping("CUSTOM_GESTURE", "custom_action")

        action = mapper.map_gesture_to_action("CUSTOM_GESTURE")
        assert action == "custom_action"

    def test_register_action_handler(self, mapper):
        """Test registering custom action handler."""
        mock_handler = Mock()
        mapper.register_action_handler("custom_action", mock_handler)

        assert "custom_action" in mapper.action_handlers
        assert mapper.action_handlers["custom_action"] == mock_handler

    def test_execute_action(self, mapper):
        """Test executing custom action."""
        # Register handler
        mock_handler = Mock()
        mapper.register_action_handler("test_action", mock_handler)

        # Execute action
        result = mapper.execute_action("test_action", "arg1", kwarg1="value1")

        assert result is True
        mock_handler.assert_called_once_with("arg1", kwarg1="value1")

    def test_execute_action_not_registered(self, mapper):
        """Test executing non-registered action."""
        result = mapper.execute_action("nonexistent_action")
        assert result is False

    def test_get_gesture_description(self, mapper):
        """Test getting gesture description."""
        desc = mapper.get_gesture_description("POINT")
        assert isinstance(desc, str)
        assert len(desc) > 0

        desc = mapper.get_gesture_description("UNKNOWN")
        assert "Unknown" in desc

    def test_get_all_mappings(self, mapper):
        """Test getting all mappings."""
        mappings = mapper.get_all_mappings()

        assert isinstance(mappings, dict)
        assert "POINT" in mappings
        assert "swipe_LEFT" in mappings

    def test_load_mappings_from_dict(self, mapper):
        """Test loading mappings from dictionary."""
        custom_mappings = {
            "CUSTOM1": "action1",
            "swipe_DIAGONAL": "diagonal_action",
            "keyboard_PEACE": "peace_action",
        }

        mapper.load_mappings_from_dict(custom_mappings)

        assert mapper.gesture_map["CUSTOM1"] == "action1"
        assert mapper.swipe_map["DIAGONAL"] == "diagonal_action"
        assert mapper.keyboard_map["PEACE"] == "peace_action"

    def test_reset_to_defaults(self, mapper):
        """Test resetting to default mappings."""
        # Modify mappings
        mapper.register_custom_mapping("CUSTOM", "custom")

        # Reset
        mapper.reset_to_defaults()

        # Check defaults are restored
        action = mapper.map_gesture_to_action("POINT")
        assert action == "move_cursor"

        # Custom mapping should be gone
        action = mapper.map_gesture_to_action("CUSTOM")
        assert action is None or action == "move_cursor"  # May reset to default structure
