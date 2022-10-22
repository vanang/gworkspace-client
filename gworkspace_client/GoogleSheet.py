import sys
import pandas as pd
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from gworkspace_client.GsuiteBase import GsuiteBase
from gworkspace_client.GoogleDrive import GoogleDrive


class GoogleSheet(GsuiteBase):
    """
    A Wrapper class of Google Sheet API for a bit of improved usability
    """

    def __init__(self, token_path: str, client_secret_path: str, url_or_id: str = None) -> None:
        super().__init__(token_path=token_path,
                       client_secret_path=client_secret_path,
                       scopes=['https://www.googleapis.com/auth/spreadsheets'])
        if url_or_id.startswith('https://docs.google.com'):
            self.sheet_url = url_or_id
            self.sheet_id = self.sheet_url.split('/')[-1]
        else:
            self.sheet_id = url_or_id
            self.sheet_url = "https://docs.google.com/spreadsheets/d/" + self.sheet_id
        self.service = self.get_service()

    def get_service(self):
        return build("sheets", "v4", credentials=self.creds)

    def read_single_sheet(self, sheet_title: str) -> pd.DataFrame:
        """
        Read a sheet and return as a pandas DataFrame format
        :param sheet_title: title of a sheet to read
        :return: dataframe format of a sheet
        """
        raw_data = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id,
                                                            range=sheet_title).execute()

        df = pd.DataFrame.from_records(raw_data.get("values", []))
        return df

    def get_sheet_titles(self) -> list:
        """
        Get titles of all sheets
        :return: list of sheet title
        """
        try:
            sheet_titles = self.service.spreadsheets().get(spreadsheetId=self.sheet_id,
                                                           fields='sheets(properties(title))').execute()
            return [v['properties']['title'] for v in sheet_titles['sheets']]

        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def create_sheet_file(self, sheet_name: str, df: pd.DataFrame, folder_id: str, sheet_title: str = 'Sheet1',
                          drive_token_path: str = '', drive_client_secret_path: str = ''):
        """
        Create a sheet file from the pandas data frame at the folder
        :param sheet_name: name of this spreadsheet file
        :param df: input data frame
        :param folder_id: id of parent folder
        :param sheet_title: title of this sheet in this spreadsheet file
        :param drive_token_path: optional token path to control drive.
                                If not specified, will use this object's token path
        :param drive_client_secret_path: optional client secret path to control drive.
                                If not specified, will use this object's client secret path
        :return:
        """

        # NOTICE: there's no way to create a sheet file directly within the specified the Drive folder
        # 1. This method creates an empty spreadsheet file at the folder beforehand
        # 2. Then fills 'Sheet1' with the dataframe contents
        if drive_token_path != '' and drive_client_secret_path != '':
            _token_path = drive_token_path
            _client_secret_path = drive_client_secret_path
        else:
            _token_path = self.token_path
            _client_secret_path = self.client_secret_path

        _gdrive = GoogleDrive(token_path=_token_path, client_secret_path=_client_secret_path)
        _sheet_id = _gdrive.create_file(folder_id=folder_id, filename=sheet_name,
                                        filetype='spreadsheet')

        self.sheet_id = _sheet_id
        self.sheet_url = "https://docs.google.com/spreadsheets/d/" + _sheet_id

        result = self.write_sheet(title=sheet_title, df=df)

        return result

    def write_sheet(self, title: str, df: pd.DataFrame):
        """
        Write or update sheet from the data frame
        :param title: title of sheet
        :param df: dataframe to write or update
        :return: result of updates
        """
        try:
            # service = self.service
            value_input_option = "USER_ENTERED"
            values = []

            # Filling NA with empty string to avoid 404 error
            df = df.fillna('')
            values.append(df.columns.to_list())
            values.extend(df.values.tolist())
            body = {
                'values': values
            }

            # building range_name: chr(66) -> 'A' to chr(66) + x
            columns_start = chr(65)
            columns_end = chr(65 + len(df.columns) - 1)
            row_end = len(df) + 1
            range_name = title + f'!{columns_start}1:{columns_end}{row_end}'

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def resize_cells(self, sheet_number: int, dimension: str, start_index: int, end_index: int, size: int):
        """
        Resize cell width or height within the specified range
        :param sheet_number: The ordinal number of sheet. The sheet_number of first sheet is 0
        :param dimension: Must be 'ROWS' or 'COLUMNS'
        :param start_index: Start index of rows or columns to resize. Resizing will be effective to start_index + 1
        :param end_index: End index of rows or columns to resize.
        :param size: The size of rows or columns in pixel unit
        :return:
        """
        try:
            body = {
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_number,
                                "dimension": dimension,
                                "startIndex": start_index,
                                "endIndex": end_index
                            },
                            "properties": {
                                "pixelSize": size
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }

            result = self.service.spreadsheets().batchUpdate(spreadsheetId=self.sheet_id, body=body).execute()

            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def add_sheet(self, sheet_title: str):
        """
        Add a new empty sheet to the current google sheet file
        :param sheet_title: the title of new empty sheet to be added
        :return:
        """

        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_title,
                            'tabColor': {
                                'blue': 0.50
                            }
                        }
                    }
                }]
            }

            result = self.service.spreadsheets().batchUpdate(spreadsheetId=self.sheet_id, body=body).execute()

            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def update_values(self, range_name: str, _values: list, value_input_option: str = "USER_ENTERED"):
        """
        Batch update the specified range with _values
        :param range_name: name of range
        :param value_input_option: the name of option for value input
        :param _values: list of value to update
            _values = [
                [
                    # Cell values ...
                ],
                # Additional rows ...
            ]
        :return: result of updates
        """

        try:
            service = self.service
            values = _values
            body = {
                'values': values
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def append_values(self, range_name: str, _values: list, value_input_option: str = "USER_ENTERED"):
        """
        Append the specified range with _values
        :param range_name: name of range
        :param value_input_option: the name of option for value input
        :param _values: list of value to update
            _values = [
                [
                    # Cell values ...
                ],
                # Additional rows ...
            ]
        :return: result of appends
        """

        try:
            service = self.service
            values = _values
            body = {
                'values': values
            }
            result = service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            print('{0} cells appended.'.format(result.get('updates').get('updatedCells')))
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
