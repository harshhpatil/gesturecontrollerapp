import time
from collections import deque

import cv2
import mediapipe as mp
import pyautogui

# ---------------- Safety ----------------
pyautogui.FAILSAFE = False

# ---------------- MediaPipe ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

# ---------------- Screen ----------------
screen_w, screen_h = pyautogui.size()

# ---------------- Calibration & Smoothing ----------------
FRAME_MARGIN = 0.15
SMOOTHING = 0.2
prev_x, prev_y = 0, 0

# ---------------- Click / Drag Control ----------------
CLICK_COOLDOWN = 0.6  # seconds
last_click_time = 0
dragging = False


# ---------------- Finger States ----------------
def get_finger_states(hand_landmarks):
    fingers = {}

    fingers["thumb"] = hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x

    fingers["index"] = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    fingers["middle"] = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    fingers["ring"] = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    fingers["pinky"] = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

    return fingers


# ---------------- Gesture Classification ----------------
def classify_gesture(fingers):
    if all(not v for v in fingers.values()):
        return "FIST"

    if all(v for v in fingers.values()):
        return "OPEN_PALM"

    if (
        fingers["thumb"]
        and fingers["index"]
        and not fingers["middle"]
        and not fingers["ring"]
        and not fingers["pinky"]
    ):
        return "PINCH"

    return "UNKNOWN"


# ---------------- Stabilization ----------------
gesture_buffer = deque(maxlen=5)


def get_stable_gesture(current):
    gesture_buffer.append(current)
    if gesture_buffer.count(current) >= 4:
        return current
    return None


# ---------------- Camera ----------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not accessible")
    exit(1)

print("✅ Gesture Mouse Control Started")

# ---------------- Main Loop ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            fingers = get_finger_states(hand)
            gesture = classify_gesture(fingers)
            stable = get_stable_gesture(gesture)

            current_time = time.time()

            # -------- Mouse Movement (OPEN PALM) --------
            if stable == "OPEN_PALM":
                index_tip = hand.landmark[8]

                # Clamp inside virtual interaction box
                x_norm = min(max(index_tip.x, FRAME_MARGIN), 1 - FRAME_MARGIN)
                y_norm = min(max(index_tip.y, FRAME_MARGIN), 1 - FRAME_MARGIN)

                # Normalize
                x_norm = (x_norm - FRAME_MARGIN) / (1 - 2 * FRAME_MARGIN)
                y_norm = (y_norm - FRAME_MARGIN) / (1 - 2 * FRAME_MARGIN)

                # Fix mirror (X-axis inversion)
                x = int((1 - x_norm) * screen_w)
                y = int(y_norm * screen_h)

                # Smooth cursor
                x = int(prev_x + (x - prev_x) * SMOOTHING)
                y = int(prev_y + (y - prev_y) * SMOOTHING)

                pyautogui.moveTo(x, y, duration=0.01)

                prev_x, prev_y = x, y

            # -------- Click / Drag (PINCH) --------
            if stable == "PINCH":
                if not dragging and (current_time - last_click_time) > CLICK_COOLDOWN:
                    pyautogui.mouseDown()
                    dragging = True
                    last_click_time = current_time

            elif stable != "PINCH" and dragging:
                pyautogui.mouseUp()
                dragging = False

            # -------- UI --------
            cv2.putText(
                frame, f"Gesture: {stable}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

    cv2.imshow("Gesture Mouse Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
