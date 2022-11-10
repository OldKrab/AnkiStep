# Run with Python 3

import datetime
import json
import os
from pathlib import Path
import requests
from appdirs import *

class OAuthStepik:
    __user_data_folder = user_data_dir('ankistep')
    __user_data_filename = '.user_data.json'
    __grand_type = 'client_credentials'

    def get_user_file(self, *args):
        path = Path(self.__user_data_folder)
        path.mkdir(parents=True, exist_ok=True)
        return open(self.__user_data_folder + self.__user_data_filename, *args)

    def __init__(self):
        self._read_user_data()

    def _read_user_data(self):
        try:
            with self.get_user_file() as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}

        self._client_id = data.get('client_id', '')
        self._client_secret = data.get('client_secret', '')
        self.__token = data.get('token', '')
        self.__expiration = data.get('expiration', datetime.datetime.min)
        if not isinstance(self.__expiration, datetime.datetime):
            self.__expiration = datetime.datetime.fromisoformat(
                str(self.__expiration))

    def _save_user_data(self):
        with self.get_user_file('w') as outfile:
            user_data: dict = {}
            user_data['client_id'] = self._client_id
            user_data['client_secret'] = self._client_secret
            user_data['token'] = self.__token
            user_data['expiration'] = self.__expiration.isoformat()
            json.dump(user_data, outfile)
            outfile.flush()

    def set_credentials(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def auth_user_password(self):
        expiration = datetime.datetime.now()

        auth = requests.auth.HTTPBasicAuth(
            self._client_id, self._client_secret)
        data = {'grant_type': self.__grand_type}
        resp = requests.post(
            'https://stepik.org/oauth2/token/', data, auth=auth)

        if resp.status_code > 300:
            raise ConnectionError("Authorization error!")

        resp = resp.json()
        self.__token = resp['access_token']
        self.__expiration = expiration + \
            datetime.timedelta(seconds=int(resp['expires_in']))
        self._save_user_data()

    def __get_headers(self):
        return {'Authorization': 'Bearer ' + self.__token, "content-type": "application/json"}

    def get_headers(self):
        expiration = datetime.datetime.now()
        if self.__expiration < expiration or self._client_id == '' or self._client_secret == '':
            self.auth_user_password()
        return self.__get_headers()
