import io
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from core_gsuite_client.GsuiteBase import GsuiteBase


class GoogleDrive(GsuiteBase):
    """
    A Wrapper class of Google Drive API for a bit of improved usability
    """

    def __init__(self, token_path: str, client_secret_path: str) -> None:
        super().__init__(token_path=token_path,
                         client_secret_path=client_secret_path,
                         scopes=['https://www.googleapis.com/auth/drive'])
        self.service = self.get_service()

    def get_service(self):
        return build("drive", "v3", credentials=self.creds)

    def list_files(self, folder_id: str, name_query: str = '') -> list:
        """
        List files and its id under the specified folder
        :param folder_id: id of the folder
        :param name_query: query string of name.
                For specific syntax, reters to https://developers.google.com/drive/api/guides/search-files
        :return: a list of tuples, composed of (file name, file id)
        """

        try:
            file_ids = []
            page_token = None
            while True:
                query = "'" + folder_id + "' in parents and mimeType!='application/vnd.google-apps.folder'"
                if len(name_query) > 0:
                    query += "and " + name_query

                response = self.service.files().list(
                    q=query,
                    fields='nextPageToken, files(id, name)',
                    pageSize=100,
                    pageToken=page_token).execute()

                for file in response.get('files', []):
                    file_ids.append((file.get('name'), file.get('id')))

                page_token = response.get('nextPageToken', None)

                if page_token is None:
                    break

        except HttpError as error:
            print(F'An error occurred: {error}')
            file_ids = None

        return file_ids

    def list_folders(self, parent_id: str, name_query: str = '') -> list:
        """
        List sub-folders under the parent folder
        :param parent_id: id of the parent folder
        :param name_query: query string of name.
                For specific syntax, reters to https://developers.google.com/drive/api/guides/search-files
        :return: a list of tuples, composed of (folder name, folder id)
        """

        try:
            folder_ids = []
            page_token = None
            while True:
                query = "'" + parent_id + "' in parents and mimeType='application/vnd.google-apps.folder'"
                if len(name_query) > 0:
                    query += "and " + name_query
                response = self.service.files().list(
                    q=query,
                    fields='nextPageToken, files(id, name)',
                    pageSize=100,
                    pageToken=page_token).execute()

                for file in response.get('files', []):
                    folder_ids.append((file.get('name'), file.get('id')))

                page_token = response.get('nextPageToken', None)

                if page_token is None:
                    break

        except HttpError as error:
            print(F'An error occurred: {error}')
            folder_ids = None

        return folder_ids

    def file_exists(self, parent_id: str, file_id_or_name: str) -> bool:
        """
        Test if the folder or file exists
        :param parent_id: id of a parent folder to search
        :param file_id_or_name: name or id of a file to be tested if exists
        :return: boolean result of test
        """

        files = self.list_files(folder_id=parent_id)
        folders = self.list_folders(parent_id=parent_id)

        files.extend(folders)

        for file_name, file_id in files:
            if file_id == file_id_or_name or file_name == file_id_or_name:
                print(f"File {file_id_or_name} exists")
                return True

        return False

    def get_file_ids(self, folder_id:str, file_name:str) -> list:
        """
        Find a list of file id, of which name matched the specifed file name
        There are probably multiple files with same name, so this returns as a list of them
        :param folder_id: parent folder id
        :param file_name: the file name that want to find
        :return: a list of tuple of (id, file name)
        """

        files = self.list_files(folder_id=folder_id)
        folders = self.list_folders(parent_id=folder_id)

        files.extend(folders)

        file_ids = []
        for _file_name, _file_id in files:
            if _file_name == file_name:
                print(f"Found {file_name}")
                file_ids.append((_file_id, _file_name))

        return file_ids

    def grant_permission(self, user_email: str, file_id: str, permission_type: str) -> list:
        """
        Grant access permission to the user on the file
        :param user_email: user email
        :param file_id: the file id
        :param permission_type: a type of permission := {reader, commenter, editor}
        :return: list of id
        """

        try:
            # create gmail api client
            service = self.service
            ids = []

            def callback(request_id, response, exception):
                if exception:
                    # Handle error
                    print(exception)
                else:
                    print(f'Request_Id: {request_id}')
                    print(F'Permission Id: {response.get("id")}')
                    ids.append(response.get('id'))

            batch = service.new_batch_http_request(callback=callback)
            user_permission = {
                'type': 'user',
                'role': permission_type,
                'emailAddress': user_email
            }
            batch.add(service.permissions().create(fileId=file_id,
                                                   body=user_permission,
                                                   fields='id', ))
            batch.execute()

        except HttpError as error:
            print(F'An error occurred: {error}')
            ids = None

        return ids

    def create_folder(self, parent_folder_id: str, sub_folder_name: str, exists_ok: bool = True) -> str:
        """
        Create a folder with under the specific folder(parent)
        :param parent_folder_id: id of parent folder
        :param sub_folder_name: name of the folder to create
        :param exists_ok: to ignore creation of folder if exists
        :return: id of the created folder
        """

        try:
            # create a subfolder under specific folder
            file_metadata = {
                'name': sub_folder_name,
                "parents": [parent_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            file = self.service.files().create(body=file_metadata, fields='id').execute()
            print("Folder ID:", file.get('id'))
            file_id = file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file_id = None

        return file_id

    def create_file(self, folder_id: str, filename: str, filetype: str) -> str:
        """
        Create a file in specified folder
        :param folder_id: id of parent folder to create this file
        :param filename: name of this file
        :param filetype:  type of this file := {'spreadsheet'}
        :return: id of the created file
        """

        try:
            # create a subfolder under specific folder
            file_metadata = {
                'name': filename,
                "parents": [folder_id],
                'mimeType': f'application/vnd.google-apps.{filetype}'
            }
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            print("file name:", filename)
            print("file id:", file.get('id'))
            file_id = file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file_id = None

        return file_id

    def copy_file(self, source_file_id: str, target_folder_id: str, filename: str) -> str:
        """
        Copy a file to the target_folder
        :param source_file_id: id of source file to be copied
        :param target_folder_id: id of parent folder
        :param filename: name of the copied file
        :return: id of the copied file
        """

        try:
            # call drive api client
            file_id = source_file_id

            file_metadata = {
                'name': filename,
                "parents": [target_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            # Copy the file to the new folder
            file = self.service.files().copy(fileId=file_id, body=file_metadata, fields='id').execute()
            copied_file_id = file.get('id')
        except HttpError as error:
            print(F'An error occurred: {error}')
            copied_file_id = None

        return copied_file_id

    def move_file_to_folder(self, file_id, folder_id) -> str:
        """
        Move a file to a folder
        :param file_id: id of the file to move
        :param folder_id: id of the folder
        :return: parent id
        """

        try:
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            # Move the file to the new folder
            file = self.service.files().update(fileId=file_id, addParents=folder_id,
                                               removeParents=previous_parents,
                                               fields='id, parents').execute()

            parents = file.get('parents')

        except HttpError as error:
            print(F'An error occurred: {error}')
            parents = None

        return parents

    def upload_file(self, folder_id:str, local_file_path:str, mimetype:str) -> str:
        """
        Upload a file to a folder
        :param folder_id: id of the folder to upload
        :param local_file_path: a path of the file to upload
        :param mimetype: mimetype of the file. ex> image/jpeg, image/png and so on.
                         For more details, please visit https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        :return: id of the uploaded file in the drive, or none if failed
        """
        filename = os.path.basename(local_file_path)

        try:
            file_metadata = {
                'name': filename,
                "parents": [folder_id],
            }
            media = MediaFileUpload(local_file_path, mimetype=mimetype)
            file = self.service.files().create(body=file_metadata, media_body=media,
                                          fields='id').execute()
            file_id = file.get('id')
            print(F'File ID: {file_id}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

        return file_id

    def download_file(self, file_id:str, download_filepath:str) -> bytes:
        """
        Download a file in byte format from the google drive
        Google Workspace Document(eg. google sheet) can be downloaded by export_file method, instead.
        :param file_id: the id of the file to download
        :param download_filepath: a full local file path including a filename
        :return: the downloaded file content in bytes format
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

            with open(download_filepath, 'wb') as out:
                out.write(file.getvalue())

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

        except IOError as ioe:
            print(f'An IO error while storing a file {ioe}')
            return None

        return file.getvalue()

    def export_file(self, file_id:str, export_path:str, mime_type:str) -> bytes:
        """
        Export a Google Workspace Document from the google drive folder and save it in the export path
        :param file_id: the id of the file to download
        :param export_path: a local file path including a filename
        :param mime_type: a mime type of file, which should conforms to Google's MIME type
                e.g. google sheet -> {'application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', ...}
                     google doc -> {'text/html', 'text/plain', 'application/rtf', 'application/pdf', 'application/epub+zip', ...}
                     and so on. For more details, visit https://developers.google.com/drive/api/guides/ref-export-formats
        :return: the exported file content in bytes format
        """
        try:
            request = self.service.files().export_media(fileId=file_id, mimeType=mime_type)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Export a file {int(status.progress() * 100)}.')

            with open(export_path, 'wb') as out:
                out.write(file.getvalue())

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None

        except IOError as ioe:
            print(f'An IO error while storing a file {ioe}')
            return None

        return file.getvalue()