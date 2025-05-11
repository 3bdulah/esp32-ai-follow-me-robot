import cv2
import mediapipe as mp
import requests
import time
import random

ESP32_IP = "172.20.10.8"
MOVE_URL = f"http://{ESP32_IP}/move"
STREAM_URL = f"http://{ESP32_IP}:81/stream"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(STREAM_URL)

last_seen_time = time.time()
in_random_mode = False
random_timer = 0
random_command = 'S'
last_command = 'S'
last_send_time = time.time()
send_interval = 0.3
steer_timer = 0
steer_duration = 0.2

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("No frame from ESP32")
        continue

    frame = cv2.resize(frame, (320, 240))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    command = 'S'

    if results.multi_hand_landmarks:
        in_random_mode = False
        last_seen_time = time.time()

        lm = results.multi_hand_landmarks[0].landmark
        cx = int(lm[mp_hands.HandLandmark.WRIST].x * 320)

        if cx < 110:
            command = 'L'
        elif cx > 210:
            command = 'R'
        else:
            command = 'F'

        print(f"[Tracking] Hand at {cx}, Sending: {command}")
        steer_timer = time.time()

    else:
        time_since = time.time() - last_seen_time
        if time_since > 10:
            if not in_random_mode:
                print("[!] Entering Random Mode")
                in_random_mode = True
                random_timer = 0

            if time.time() - random_timer > 5:
                random_command = random.choice(['F', 'L', 'R'])
                random_timer = time.time()
                print(f"[Random] New command: {random_command}")

            command = random_command
        else:
            print("[No Hand] Sending Stop")
            command = 'S'

    # Short L/R command to 0.2s only
    if command in ['L', 'R'] and time.time() - steer_timer > steer_duration:
        command = 'S'

    now = time.time()
    if command != last_command or (now - last_send_time > send_interval):
        try:
            requests.get(f"{MOVE_URL}?dir={command}", timeout=0.05)
            last_command = command
            last_send_time = now
        except Exception as e:
            print("Failed to send command:", e)

    cv2.putText(frame, f"CMD: {command}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Follow Me", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()