# ============================================================================
# COMPLETE OPTIMIZED CODE FOR GESTURE CONTROL
# Copy each section to the corresponding file in your project
# ============================================================================

# Cursor movement
CURSOR_SMOOTHING = 0.6  # Higher = faster cursor (0.0-1.0)

# Scroll behavior
SCROLL_MULTIPLIER = 180  # Pixels per scroll unit
SCROLL_DEADZONE = 0.015  # Ignore small movements
SCROLL_MAX_AMOUNT = 80  # Maximum scroll per frame

# Swipe detection
SWIPE_THRESHOLD = 0.18  # Minimum distance for swipe
SWIPE_BUFFER_SIZE = 10  # Frames to track

# Drag
DRAG_HOLD_TIME = 0.4  # Seconds to hold before dragging

# Click
CLICK_COOLDOWN = 0.7  # Seconds between clicks

# Pause
PAUSE_COOLDOWN = 1.0  # Seconds between pause toggles

# Gesture Stabilization
GESTURE_BUFFER_SIZE = 5  # Frames to buffer
GESTURE_THRESHOLD = 3  # Minimum occurrences to confirm

# Hand Tracking
MAX_NUM_HANDS = 1
MODEL_COMPLEXITY = 0  # 0 or 1 (0 is faster)
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# Display
SHOW_FPS = True
FRAME_SKIP = 2  # Display every Nth frame (1 = all frames)

# Camera
CAMERA_INDEX = 1
