import logging
import time

import cv2
import face_recognition
import gspread
import mediapipe as mp
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)


class GestureRecognition:
    def __init__(self, drive_uploader, folder_id):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.gesture_start_time = None
        self.last_gesture = None
        self.drive_uploader = drive_uploader
        self.countdown_running = False
        self.folder_id = folder_id
        self.gesture_held = False
        self.countdown_start_time = None  # Add this line
        self.known_encodings = self.load_known_encodings('facial_encodings.txt')
        self.spreadsheet_id = "1QXmAMtjUqZTch6MtifXJzoPDeOPcPMhZMgN0fw9K9WI"

    @staticmethod  #FOR TEST PURPOSES
    def load_known_encodings(filename):
        known_encodings = []
        with open(filename, 'r') as f:
            for line in f:
                # Convert the string representation of the list to a list
                encoding = list(map(float, line.strip()[1:-1].split(', ')))
                known_encodings.append(encoding)
        return known_encodings

    @staticmethod  #FOR TEST PURPOSES
    def compare_faces(known_encodings, face_encoding_to_check, tolerance=0.6):
        return face_recognition.compare_faces(known_encodings, face_encoding_to_check, tolerance)

    @staticmethod
    def get_student_data(spreadsheet_id, credentials_file):
        # Use the credentials file to authenticate and create a client
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(creds)

        # Open the spreadsheet and get the first sheet
        sheet = client.open_by_key(spreadsheet_id).sheet1

        # Get all records of the data
        data = sheet.get_all_values()

        # Get the data of each row
        rows_data = [row for row in data]

        return rows_data

    def recognize_gesture(self, landmarks):
        thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

        fingertips = [landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP],
                      landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                      landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP],
                      landmarks[self.mp_hands.HandLandmark.PINKY_TIP]]

        base_joints = [landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP],
                       landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
                       landmarks[self.mp_hands.HandLandmark.RING_FINGER_MCP],
                       landmarks[self.mp_hands.HandLandmark.PINKY_MCP]]

        palm_base = landmarks[self.mp_hands.HandLandmark.WRIST]

        if all(fingertip.y < base_joint.y for fingertip, base_joint in zip(fingertips, base_joints)):
            return "Raised Hand"

        x_diff_thumb_palm = thumb_tip.x - palm_base.x
        y_diff_thumb_palm = thumb_tip.y - palm_base.y
        distance_thumb_palm = (x_diff_thumb_palm ** 2 + y_diff_thumb_palm ** 2) ** 0.5

        if all(base_joint.y < palm_base.y for base_joint in base_joints) and distance_thumb_palm < 0.2:
            return "Fist"

        x_diff = thumb_tip.x - index_finger_tip.x
        y_diff = thumb_tip.y - index_finger_tip.y
        distance = (x_diff ** 2 + y_diff ** 2) ** 0.5

        if distance < 0.2 and all(
                fingertip.y < base_joint.y for fingertip, base_joint in zip(fingertips[1:], base_joints[1:])):
            return "OK"

        return "Unknown Gesture"

    def run_countdown(self, image):
        for i in range(3, 0, -1):
            start_time = time.time()
            while time.time() - start_time < 1:
                if not self.gesture_held:
                    self.countdown_running = False
                    return False
                time.sleep(0.1)

            image_copy = image.copy()
            cv2.putText(image_copy, f"Countdown: {i}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)
            cv2.imshow('Gesture Recognition', image_copy)
            cv2.waitKey(1)

        if self.gesture_held:
            image_copy = image.copy()
            image_path = "evidence.png"
            cv2.imwrite(image_path, image_copy)

            if self.drive_uploader.upload_photo(image_path, self.folder_id):
                print("Evidence uploaded.")
            else:
                print("An error occurred while trying to upload the evidence.")

            if self.last_gesture == "Fist":
                for i in range(10, 0, -1):
                    start_time = time.time()
                    while time.time() - start_time < 1:
                        time.sleep(0.1)

                    image_copy = image.copy()

                    # Set the text and calculate its size
                    text = f"{i} SECONDS LEFT!"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 2
                    thickness = 5
                    color = (0, 0, 255)  # Red color in BGR

                    # Calculate the size of the text box
                    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

                    # Calculate the center position of the text
                    text_x = (image_copy.shape[1] - text_size[0]) // 2
                    text_y = (image_copy.shape[0] + text_size[1]) // 2

                    # Put the text on the image
                    cv2.putText(image_copy, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
                    cv2.imshow('Gesture Recognition', image_copy)
                    cv2.waitKey(1)
                self.countdown_running = False
                self.gesture_held = False
                return False
        self.countdown_running = False
        return False

    def run(self):
        cap = cv2.VideoCapture(0)
        self.gesture_held = False

        while cap.isOpened():

            success, self.image = cap.read()
            if not success:
                continue

            self.image = cv2.cvtColor(cv2.flip(self.image, 1), cv2.COLOR_BGR2RGB)
            results = self.hands.process(self.image)

            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
            gesture = "Unknown Gesture"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(self.image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    gesture = self.recognize_gesture(hand_landmarks.landmark)
                    cv2.putText(self.image, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            if gesture != self.last_gesture:
                self.gesture_start_time = time.time()
                self.last_gesture = gesture
                self.gesture_held = True
                self.countdown_start_time = time.time() if gesture != "Unknown Gesture" else None
                self.countdown_running = gesture != "Unknown Gesture"
                logging.info(f"New gesture detected: {gesture}")
            elif self.countdown_running and (time.time() - self.countdown_start_time > 3):
                self.run_countdown(self.image)
                time.sleep(1)
                if self.last_gesture == "Fist":
                    # Capture a frame from the camera after the countdown
                    success, self.image = cap.read()
                    if not success:
                        print("Failed to capture frame from camera.")
                        return

                    # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
                    rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    user_face_encoding = face_recognition.face_encodings(rgb_image)
                    if user_face_encoding:  # Check if a face was found
                        user_face_encoding = user_face_encoding[0]  # Get the first item in the list

                        student_data = self.get_student_data(self.spreadsheet_id, 'credentials.json')

                        student_facial_encodings_str = student_data[5][2]
                        student_face_encodings = np.array(
                            list(map(float, student_facial_encodings_str.strip()[1:-1].split(', '))))
                        print(student_face_encodings)
                        match = face_recognition.compare_faces([student_face_encodings], user_face_encoding)
                        print(match)
                    else:
                        print("No face found in the image. Student did not come back from the toilet in time.")

            if self.countdown_running:
                countdown_value = 3 - int(time.time() - self.countdown_start_time)
                cv2.putText(self.image, f"Countdown: {countdown_value}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2, cv2.LINE_AA)

            cv2.imshow('Gesture Recognition', self.image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
