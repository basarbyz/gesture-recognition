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
