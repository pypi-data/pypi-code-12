from myshows.urls import *
from myshows.exceptions import *

VERSION = '0.0.3.1'
SHOW_STATUS = ['watching', 'cancelled', 'later', 'remove']

class session(object):
    def __init__(self):
        from requests import Session
        self._session = Session()

    def md5(self, string):
        from hashlib import md5
        return md5(string.encode('utf-8')).hexdigest()

    def login(self, login, password):
        if not login:
            raise ValueError('Empty login')
        if not password:
            raise ValueError('Empty password')

        credentials = {}
        credentials['login'] = login
        credentials['password'] = self.md5(password)

        url = self.__join(LOGIN) + '?'
        return self.__call(url, params=credentials, json=False)

    def __call(self, url, params=None, json=True):
        try:
            response = self._session.get(url, params=params)
        except:
            raise MyShowsException()

        code = response.status_code
        if code == 401:
            raise MyShowsAuthentificationRequiredException('Auth Required')
        elif code == 403:
            raise MyShowsAuthentificationFailedException('Auth Failed')
        elif code == 404:
            raise MyShowsInvalidParametersException()

        if json == False:
            return response
        return response.json()

    def __join(self, path):
        if not path:
            return None
        from urllib.parse import urljoin
        return urljoin(HOST, path)

    def profile(self):
        url = self.__join(PROFILE)
        return self.__call(url)

    def profile_shows(self, shows_id=None):
        url = self.__join(PROFILE_SHOWS) + str(shows_id) + '/' if shows_id else self.__join(PROFILE_SHOWS)
        return self.__call(url)

    def profile_news(self):
        url = self.__join(PROFILE_NEWS)
        return self.__call(url)

    # status = ['watching', 'cancelled', 'later', 'remove']
    def profile_shows_status(self, shows_id, status):
        if status not in SHOW_STATUS:
            return None
        if not shows_id:
            return None
        url = self.__join(PROFILE_SHOWS) + str(shows_id) + '/' + status
        response = self.__call(url, json=False)
        return response

    def profile_next(self):
        url = self.__join(PROFILE_NEXT)
        return self.__call(url)

    def profile_unwatched(self):
        url = self.__join(PROFILE_UNWATCHED)
        return self.__call(url)

    # without auth methods 
    def shows(self, shows_id):
        url = self.__join(SHOWS) + str(shows_id)
        return self.__call(url)

    def user_profile(self, username):
        if not username:
            return None
        url = self.__join(PROFILE) + username
        return self.__call(url)

    def search(self, q):
        url = self.__join(SEARCH)
        data = {'q':q}
        return self.__call(url, data)

    def genres(self):
        url = self.__join(GENRES)
        return self.__call(url)
