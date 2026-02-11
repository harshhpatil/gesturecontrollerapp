from collections import deque

import cv2
import mediapipe as mp

# ---------------- MediaPipe Setup ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)


# ---------------- Finger Detection ----------------
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

print("✅ Camera started")

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

            if stable:
                cv2.putText(
                    frame,
                    f"Gesture: {stable}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                print("Stable Gesture:", stable)

    cv2.imshow("Gesture Stage 1", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
