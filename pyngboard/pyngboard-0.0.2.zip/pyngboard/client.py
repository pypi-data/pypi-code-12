from .credentials import Credentials

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from urllib import urlencode

PINGBOARD_OAUTH_URL='https://app.pingboard.com/oauth'
PINGBOARD_TOKEN_URL=PINGBOARD_OAUTH_URL + '/token'
PINGBOARD_REFRESH_URL=PINGBOARD_OAUTH_URL + '/refresh_token'

PINGBOARD_API_URL='https://app.pingboard.com/api/v2/'

class PingboardClient:

    def __init__(self, **kwargs):

        if 'client_id' in kwargs and 'client_secret' in kwargs:
            self.__credentials = Credentials(**kwargs)
        else:
            self.__credentials = kwargs.get('credentials')
            if self.__credentials is None:
                self.__credentials = Credentials()

        if not self.__credentials.load():
            raise Exception("Could not load credentials from any source")

        self.__init_oauth()

    def __init_oauth(self):
        self.__client = BackendApplicationClient(client_id=self.__credentials.client_id)
        self.__session = OAuth2Session(client=self.__client)
        self.__token = self.__session.fetch_token(token_url=PINGBOARD_TOKEN_URL,
                client_id=self.__credentials.client_id,
                client_secret=self.__credentials.client_secret)
        self.__session = OAuth2Session(client=self.__client,
                token=self.__token,
                auto_refresh_url=PINGBOARD_REFRESH_URL,
                token_updater=self.__set_token)

    def __set_token(self, token):
        self.__token = token

    def __request(self, method, url, body=None):
        return self.__session.request(method, PINGBOARD_API_URL + url, body);

    def get_user(self, user_id, *includes):
        response = self.__request("GET", "users/" + str(user_id) + "?include=" + ",".join(includes))
        if response.status_code is 200:
            return response.json()['users'][0]

        return None

    def get_users(self, **kwargs):
        response = self.__request("GET", "users?" + urlencode(kwargs, False))
        if response.status_code is 200:
            return response.json()['users']

        return None

    def get_group(self, group_id, *includes):
        response = self.__request("GET", "groups/" + str(group_id) + "?include=" + ",".join(includes))
        if response.status_code is 200:
            return response.json()['groups'][0]

        return None

    def get_groups(self, **kwargs):
        response = self.__request("GET", "groups?" + urlencode(kwargs, False))
        if response.status_code is 200:
            return response.json()['groups']

        return None
