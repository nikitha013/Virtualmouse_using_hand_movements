import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr
import numpy as np
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
    model_complexity=1  
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

screen_width, screen_height = pyautogui.size()

recognizer = sr.Recognizer()

smoothening = 5
prev_x, prev_y = 0, 0

def voice_command():
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print("Command received:", command)
        if "click" in command:
            pyautogui.click()
        elif "double click" in command:
            pyautogui.doubleClick()
        elif "scroll up" in command:
            pyautogui.scroll(10)
        elif "scroll down" in command:
            pyautogui.scroll(-10)
    except sr.UnknownValueError:
        print("Could not understand the command.")
    except sr.RequestError:
        print("Could not request results, check your internet connection.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    
    if w != h:
        new_size = min(w, h)
        frame = cv2.resize(frame, (new_size, new_size))
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            index_finger_tip = hand_landmarks.landmark[8]
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            screen_x = int(np.interp(index_finger_tip.x, [0, 1], [0, screen_width]))
            screen_y = int(np.interp(index_finger_tip.y, [0, 1], [0, screen_height]))
            
            
            cur_x = prev_x + (screen_x - prev_x) / smoothening
            cur_y = prev_y + (screen_y - prev_y) / smoothening
            pyautogui.moveTo(cur_x, cur_y)
            prev_x, prev_y = cur_x, cur_y
            
            thumb_tip = hand_landmarks.landmark[4]
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            
            
            if abs(thumb_x - x) < 40 and abs(thumb_y - y) < 40:
                pyautogui.click()
                cv2.putText(frame, "Click", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("AI Virtual Mouse", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('v'):
        voice_command()
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
