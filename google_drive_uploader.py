from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import traceback


class GoogleDriveUploader:
    def __init__(self, credentials_file, root_folder_id):
        self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
        self.root_folder_id = root_folder_id

    def create_folder(self, folder_name, parent_folder_id):
        creds = self.credentials
        try:
            # create drive api client
            service = build("drive", "v3", credentials=creds)
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id]
            }

            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, fields="id").execute()
            print(f'Folder ID: "{file.get("id")}".')
            return file.get("id")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def upload_photo(self, image_path, folder_id):
        try:
            service = build('drive', 'v3', credentials=self.credentials)
            file_metadata = {
                'name': 'gesture.png',
                'mimeType': 'image/png',
                'parents': [folder_id]
            }
            media = MediaFileUpload(image_path, mimetype='image/png')
            file = service.files().create(
                body=file_metadata,
                media_body=media,
            ).execute()
            return True
        except Exception as e:
            print(f"An error occurred while trying to upload the file: {e}")
            traceback.print_exc()  # Print the full stack trace
            return False
