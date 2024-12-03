import cv2
import mediapipe as mp
import requests
import os
from PIL import Image

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

SERVER_URL = "http://127.0.0.1:8000"  # Replace with the server URL

prev_state = None
captured_face_path = "captured_face.jpg"
data_image_path = "data.jpg"

def crop_largest_face(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        cropped_face = frame[y:y+h, x:x+w]
        Image.fromarray(cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)).save(captured_face_path)
        return True
    return False

cap = cv2.VideoCapture(0)

with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                current_state = "Open" if sum(1 for i in [8, 12, 16, 20] if landmarks[i].y < landmarks[i - 2].y) > 3 else "Closed"

                if prev_state and current_state != prev_state:
                    if current_state == "Closed":
                        if crop_largest_face(frame):
                            files = {"face_image": open(captured_face_path, "rb"), "data_image": open(data_image_path, "rb")}
                            response = requests.post(f"{SERVER_URL}/save-images/", files=files)
                            print(response.json())
                    elif current_state == "Open":
                        if crop_largest_face(frame):
                            files = {"face_image": open(captured_face_path, "rb")}
                            response = requests.get(f"{SERVER_URL}/get-data-image/", files=files)
                            if response.status_code == 200:
                                with open("returned_data.jpg", "wb") as f:
                                    f.write(response.content)
                                print("Received matching data image and saved as returned_data.jpg")
                                img = cv2.imread("returned_data.jpg")
                                cv2.imshow("Received Image", img)  
                     
                            else:
                                print(response.json())

                prev_state = current_state

        cv2.imshow("Hand Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
