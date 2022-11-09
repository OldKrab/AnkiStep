# Run with Python 3

import datetime
import json
import requests


class OAuthStepic:
    __user_data_filename = 'user_data.json'
    __grand_type = 'client_credentials'

    _username = None
    _client_id = None
    _client_secret = None
    __token = None
    __expiration = None
    __refresh_token = None

    def __init__(self):
        self._read_user_data()

    def _read_user_data(self):
        try:
            with open(self.__user_data_filename) as json_file:
                data = json.load(json_file)
                self._username = data['username']
                self._client_id = data['client_id']
                self._client_secret = data['client_secret']
                if 'refresh_token' in data:
                    self.__refresh_token = data['refresh_token']
                if 'expiration' in data:
                    self.__expiration = data['expiration']
                if 'token' in data:
                    self.token = data['token']
        except (FileNotFoundError, FileNotFoundError) as e:
            print("File open error")

    def _save_user_data(self):
        with open(self.__user_data_filename, 'w') as outfile:
            user_data: dict = {}
            user_data['username'] = self._username
            user_data['client_id'] = self._client_id
            user_data['client_secret'] = self._client_secret
            user_data['token'] = self.__token
            user_data['expiration'] = self.__expiration
            user_data['refresh_token'] = self.__refresh_token
            json.dump(user_data, outfile)
            outfile.flush()

    def set_credentials(self, client_id, client_secret, username=None):
        if username is not None:
            self._username = username
        self._client_id = client_id
        self._client_secret = client_secret
        self._save_user_data()

    def auth_user_password(self, password=None):
        try:
            expiration = datetime.datetime.now().timestamp()
            if password:
                data = {'grant_type': self.__grand_type,
                        'client_id': self._client_id,
                        'secret_id': self._client_secret,
                        'username': self._username,
                        'password': password}
                resp = requests.post('https://stepik.org/oauth2/token/', data)
            else:
                auth = requests.auth.HTTPBasicAuth(self._client_id, self._client_secret)
                data = {'grant_type': self.__grand_type}
                resp = requests.post('https://stepik.org/oauth2/token/', data, auth=auth)

            assert resp.status_code < 300

            resp = resp.json()
            self.__token = resp['access_token']
            self.__expiration = expiration + datetime.timedelta(seconds=int(resp['expires_in'])).microseconds
            self.__refresh_token = None
            if 'refresh_token' in resp:
                self.__refresh_token = resp['refresh_token']
            self._save_user_data()
        except (AssertionError, Exception) as e:
            return {'Error': 'Check your authentication.', 'error': e}

        return self.__get_headers()

    def refresh_client(self):
        try:
            expiration = datetime.datetime.now().timestamp()
            data = {'grant_type': 'refresh_token',
                    'client_id': self._client_id,
                    'secret_id': self._client_secret,
                    'refresh_token': self.__refresh_token}

            resp = requests.post('https://stepik.org/oauth2/token/', data).json()

            assert resp.status_code < 300

            self.__token = resp['access_token']
            self.__refresh_token = resp['refresh_token']
            self.__expiration = expiration + datetime.timedelta(seconds=int(resp['expires_in'])).total_seconds() * 1e6
            if 'refresh_token' in resp:
                self.__refresh_token = resp['refresh_token']
            self._save_user_data()
        except AssertionError:
            return {'Error': 'Check your authentication.'}

        return self.__get_headers()

    def __get_headers(self):
        return {'Authorization': 'Bearer ' + self.__token, "content-type": "application/json"}

    def get_headers(self):
        expiration = datetime.datetime.now().timestamp()
        if self.__expiration < expiration:
            if self.__refresh_token is not None:
                return self.refresh_client()
            else:
                return self.auth_user_password()
        else:
            return self.__get_headers()

#  HOW-TO
# if __name__ == "__main__":
#     o_auth = OAuth_stepic()
#     o_auth.set_credentials('L8AdPGUc0iJpzFAshAPovBsaWcuLHazUxbFCqDY4', 'BusVGcFHdk1zkshMnfSobJVmiL0AYMYINll9wnJ9rq62BSPo5M3GqAr7CcMB1ysKEWuJvrsVpIC7BSEowdeUDi5bQUyhxIVDGcFtsWXcXt6cFOoGNNC1GJ434QQDeSk9')
#     header = o_auth.auth_user_password()
#     print(header)

