# Gesture Controller - Hand Gesture-Based Computer Control

[![CI Pipeline](https://github.com/harshhpatil/gesturecontrollerapp/workflows/CI%20Pipeline/badge.svg)](https://github.com/harshhpatil/gesturecontrollerapp/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, modular gesture-controlled computer system that uses webcam video to track hand movements in real-time and convert them into system-level actions. Control your computer with intuitive hand gestures - no mouse or keyboard required!

## ✨ Features

### Core Capabilities
- **Mouse Control**: Precise cursor movement using index finger tracking
- **Left Click**: Pinch gesture (thumb + index finger)
- **Right Click**: Open palm gesture
- **Double Click**: Victory/Peace gesture (index + middle fingers)
- **Scrolling**: Two-finger pinch with vertical motion or three fingers
- **Dragging**: Index + middle finger pinch while moving or closed fist
- **Swipe Navigation**: Browser back/forward with directional swipes
- **Pause Control**: 
  - **Harsh Pause**: Two hands open (immediate stop)
  - **Regular Pause/Resume**: Thumbs up gesture toggle

### Keyboard Support
- **Keyboard Shortcuts**: Copy (Ctrl+C), Paste (Ctrl+V), Undo (Ctrl+Z), Redo (Ctrl+Y)
- **Text Typing**: Letter and number input support
- **Custom Hotkeys**: Configurable keyboard combinations

### Advanced Features
- **Two-Handed Gestures**: Harsh pause control with both hands
- **Enhanced Error Handling**: Robust gesture recognition with validation
- **Gesture Stabilization**: Reduces false triggers with buffering
- **Smooth Cursor Movement**: Exponential smoothing for natural control
- **Cross-Platform**: Works on Linux and Windows
- **Configurable Settings**: Extensive customization options
- **Real-time FPS Display**: Performance monitoring
- **Visual Feedback**: On-screen gesture and status display with color coding

## 📋 Requirements

- **Python**: 3.8 or higher
- **Webcam**: Built-in or external USB camera
- **Operating System**: Linux or Windows
- **Processor**: Recommended dual-core or better

## 🚀 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/harshhpatil/gesturecontrollerapp.git
cd gesturecontrollerapp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install as package (optional)
pip install -e .
```

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

## 📖 Usage

### Basic Usage

```bash
# Using Python module
python -m gesture_controller.main

# Or if installed as package
gesture-controller
```

### Controls

| Gesture | Action | Description |
|---------|--------|-------------|
| **Point** (Index finger) | Move Cursor | Point to control cursor |
| **Pinch** (Thumb + Index) | Left Click | Pinch fingers together |
| **Palm** (All fingers) | Right Click | Open hand |
| **Victory** (Index + Middle) | Double Click | V sign |
| **Fist** (All closed) | Start Drag | Close fist |
| **Three Fingers** | Scroll | Three fingers up |
| **Two Hands Open** | **Harsh Pause** | Both hands with open palms (immediate stop) |
| **Thumbs Up** | Pause/Resume | Toggle control or resume from harsh pause |
| **Swipe Left** | Navigate Back | Browser back |
| **Swipe Right** | Navigate Forward | Browser forward |

**Pause Control:**
- 🔴 **Harsh Pause** (Red): Two hands open - immediate stop, requires thumbs up to resume
- 🟡 **Regular Pause** (Yellow): Single thumbs up - toggles pause on/off
- 🟢 **Active** (Green): System is active and processing gestures

Press **ESC** to exit.

## ⚙️ Configuration

```python
from gesture_controller.config import Config

config = Config()
config.CAMERA_INDEX = 0
config.CURSOR_SMOOTHING = 0.7
config.SHOW_FPS = True
```

### Key Settings

- `CAMERA_INDEX`: Camera device (default: 0)
- `MAX_NUM_HANDS`: Maximum hands to detect (default: 2)
- `CURSOR_SMOOTHING`: Movement speed (0.0-1.0)
- `PINCH_THRESHOLD`: Pinch sensitivity
- `GESTURE_BUFFER_SIZE`: Stabilization frames
- `TWO_HANDS_MIN_FINGERS`: Minimum fingers for two-handed pause (default: 3)
- `HARSH_PAUSE_ENABLED`: Enable two-handed harsh pause (default: True)
- `PAUSE_COOLDOWN`: Seconds between pause toggles (default: 1.0)
- `SHOW_FPS`: Display frame rate
- `DEBUG_MODE`: Enable debug output

## 🏗️ Architecture

```
gesture_controller/
├── main.py                 # Entry point & orchestration
├── hand_detector.py        # MediaPipe hand detection
├── gesture_recognizer.py   # Gesture recognition
├── control_mapper.py       # Gesture-to-action mapping
├── os_controller.py        # OS-level control (pynput)
└── config.py              # Configuration management
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=gesture_controller
```

### Code Quality

```bash
# Format code
black gesture_controller/ tests/
isort gesture_controller/ tests/

# Lint
flake8 gesture_controller/ tests/
pylint gesture_controller/
```

## 🔧 Troubleshooting

**Camera not opening:**
- Check camera is not in use
- Try different `CAMERA_INDEX` values
- Verify camera permissions

**Low FPS:**
- Close resource-intensive apps
- Reduce resolution
- Set `MODEL_COMPLEXITY = 0`
- Ensure good lighting

**Hand not detected:**
- Improve lighting
- Keep hand in view
- Reduce `MIN_DETECTION_CONFIDENCE`

**False triggers:**
- Increase `GESTURE_BUFFER_SIZE`
- Adjust cooldown times

## 🎯 Future Enhancements

- Multi-hand support
- Custom gesture training
- Voice command integration
- Mobile app control
- Gesture macros
- VR/AR integration
- AI-powered prediction
- Multi-language layouts

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **MediaPipe**: Hand tracking
- **OpenCV**: Computer vision
- **pynput**: Cross-platform input
- **PyAutoGUI**: Screen automation

## 📧 Contact

**Harsh Patil**
- GitHub: [@harshhpatil](https://github.com/harshhpatil)

---

**Made with ❤️ for hands-free computing**
