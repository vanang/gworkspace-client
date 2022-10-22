import os
import abc

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GsuiteBase:
    def __init__(self, token_path: str, client_secret_path: str, scopes: list):
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self.creds = self.get_token(scopes=scopes)

    def get_token(self, scopes: str) -> object:
        """
        Get an auth token and save as a local token
        :return: a credential object
        """

        creds = None
        SCOPES = scopes

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    @abc.abstractmethod
    def get_service(self):
        pass
