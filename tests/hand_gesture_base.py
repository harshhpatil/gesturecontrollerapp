import cv2
import mediapipe as mp

# --------- MediaPipe Setup ----------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)


# --------- Finger Detection ----------
def get_finger_states(hand_landmarks):
    fingers = {}

    # Thumb (x-axis check)
    fingers["thumb"] = hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x

    # Other fingers (y-axis check)
    fingers["index"] = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    fingers["middle"] = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    fingers["ring"] = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    fingers["pinky"] = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

    return fingers


# --------- Camera ----------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not accessible")
    exit(1)

print("✅ Camera started")

# --------- Main Loop ----------
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

            # Display finger states
            text = " ".join([f"{k}:{'1' if v else '0'}" for k, v in fingers.items()])
            cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            print(fingers)

    cv2.imshow("Hand Gesture Base", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
