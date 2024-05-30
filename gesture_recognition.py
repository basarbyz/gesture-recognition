import cv2
import mediapipe as mp
import time
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google_drive_uploader as GoogleDriveUploader

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

        if all(fingertip.y < base_joint.y for fingertip, base_joint in zip(fingertips, base_joints)):
            return "Raised Hand"

        if all(fingertip.y > landmarks[self.mp_hands.HandLandmark.WRIST].y for fingertip in fingertips):
            return "Fist"

        x_diff = thumb_tip.x - index_finger_tip.x
        y_diff = thumb_tip.y - index_finger_tip.y
        distance = (x_diff ** 2 + y_diff ** 2) ** 0.5
        if distance < 0.05:
            return "OK"

        return "Unknown Gesture"

    def start_countdown(self, image):
        if self.last_gesture == "Unknown Gesture":
            return False
        self.countdown_running = True
        for i in range(5, 0, -1):
            start_time = time.time()
            while time.time() - start_time < 1:
                if not self.gesture_held:
                    self.countdown_running = False
                    return False
                time.sleep(0.1)

            # Display the countdown on the window
            image_copy = image.copy()
            cv2.putText(image_copy, f"Countdown: {i}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)
            cv2.imshow('Gesture Recognition', image_copy)
            cv2.waitKey(1)

        if self.gesture_held:
            # Create a copy of the image to display the captured message
            image_copy = image.copy()
            cv2.putText(image_copy, "Evidence captured!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)
            # Save the image to a file
            image_path = "evidence.png"
            cv2.imwrite(image_path, image_copy)
            # Upload the image to Google Drive
            self.drive_uploader.upload_photo(image_path, self.folder_id)
        else:
            self.countdown_running = False
            return False
        self.countdown_running = False
        self.gesture_held = False
        return False

    def run(self):
        cap = cv2.VideoCapture(0)
        self.gesture_held = False

        while cap.isOpened():
            start_time = time.time()  # Start time of the current frame

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
            elif self.countdown_running and (time.time() - self.countdown_start_time > 5):
                if self.gesture_held:
                    image_copy = self.image.copy()
                    cv2.putText(image_copy, "Evidence captured!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                cv2.LINE_AA)
                    image_path = "evidence.png"
                    cv2.imwrite(image_path, image_copy)
                    self.drive_uploader.upload_photo(image_path, self.folder_id)
                self.countdown_running = False
                self.gesture_held = False

            if self.countdown_running:
                countdown_value = 5 - int(time.time() - self.countdown_start_time)
                cv2.putText(self.image, f"Countdown: {countdown_value}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2, cv2.LINE_AA)

            cv2.imshow('Gesture Recognition', self.image)
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break

            time_elapsed = time.time() - start_time  # Time taken to process the current frame
            if time_elapsed < 0.1:  # If processed faster than the frame time for 10 FPS
                time.sleep(0.1 - time_elapsed)  # Sleep for the remaining time to match the frame time for 10 FPS

        cap.release()
        cv2.destroyAllWindows()
