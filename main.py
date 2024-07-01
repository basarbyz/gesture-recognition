from google_drive_uploader import GoogleDriveUploader
from gesture_recognition import GestureRecognition
from google.oauth2 import service_account
from googleapiclient.discovery import build


def check_permissions(credentials_file, folder_id):
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        service = build('drive', 'v3', credentials=credentials)

        # Check if we can access the folder
        folder = service.files().get(fileId=folder_id, fields='id, name').execute()
        print(f"Successfully accessed folder: {folder['name']} ({folder['id']})")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



'''
if __name__ == "__main__":
    credentials_file = "credentials.json"
    root_folder_id = "12lidi-l-tWTDCAz-Uv49nA4JWZnQ4-8q"  # The ROOT Folder ID
    if check_permissions(credentials_file, root_folder_id):
        print("Permissions are correctly set.")
        drive_uploader = GoogleDriveUploader(credentials_file,
                                             root_folder_id)  # Create an instance of the GoogleDriveUploader class
        if root_folder_id:
            student_folder_id = drive_uploader.create_folder("Student",
                                                             root_folder_id)  # Create a folder for the student
            evidences_folder_id = drive_uploader.create_folder("Evidences",
                                                               student_folder_id)  # Create a folder for the evidences
            test_image_path = "test_image.jpg"  # Replace with the path to your test image
            if drive_uploader.upload_photo(test_image_path, evidences_folder_id):
                print("Test image uploaded.")
            gr = GestureRecognition(drive_uploader, evidences_folder_id)
            gr.run()
        else:
            print("An error occurred while trying to create the folder")
    else:
        print("Permissions are not set correctly.")


 def test_face_comparison():
    # Load the known encodings
    known_encodings = load_known_encodings('facial_encodings.txt')

    # Capture a frame from the camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Get the facial encoding of the face in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the face encoding with the known encodings
            matches = compare_faces(known_encodings, face_encoding)
            if True in matches:
                # Draw a square around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                # Print "442442" near the face
                cv2.putText(frame, "442442", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "Face not found", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
'''
