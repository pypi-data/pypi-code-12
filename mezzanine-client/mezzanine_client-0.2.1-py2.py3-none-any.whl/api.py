import os
import sys
import json
from requests_oauthlib import OAuth2Session

# Python 2 and 3 compatible input
from builtins import input

from .config import Parser, settings
from .errors import MezzanineValueError


# OAuth Redirect URI
# Must match the value supplied when creating the OAuth App!
# Ideally should be 'urn:ietf:wg:oauth:2.0:oob' but currently unsupported by django-oauth-toolkit
REDIRECT_URI = 'https://httpbin.org/get'


class MezzanineCore(object):
    """
    Mezzanine API Client SDK
    """

    def __init__(self, credentials=None, api_url=None, version=None):
        """
        Create new instance of Mezzanine Client
        :param credentials: tuple (app_id, app_secret)
        :param api_url: str url to Mezzanine REST API
        :param version: str version of the REST API (currently unimplemented)
        """
        super(MezzanineCore, self).__init__()

        # Allow insecure transport protocol (HTTP) for development/testing purposes
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        # Check for OAuth2 credentials
        if credentials and type(credentials) is tuple:
            self.client_id = credentials[0]
            self.client_secret = credentials[1]
        else:
            try:
                self.client_id = os.environ['MZN_ID']
                self.client_secret = os.environ['MZN_SECRET']
            except KeyError:
                print('Error: API credentials were not provided.\n'
                      'Please set environment variables MZN_ID and MZN_SECRET with your OAuth app ID and secret.')
                sys.exit(1)

        credentials_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        # API URLs
        self.api_url = api_url or 'http://127.0.0.1:8000/api'
        self.auth_url = self.api_url + '/oauth2/authorize'
        self.token_url = self.api_url + '/oauth2/token/'
        self.refresh_url = self.token_url

        # Set refresh token from cache (if exists)
        refresh_token = settings.refresh_token

        # Initialise session
        self.session = OAuth2Session(self.client_id, redirect_uri=REDIRECT_URI, auto_refresh_url=self.refresh_url)
        self.session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

        # Authenticate
        if not refresh_token:
            authorization_url, state = self.session.authorization_url(self.auth_url)
            print("Please click to authorize this app: {}".format(authorization_url))
            code = input("Paste the authorization code (args > code) from your browser here: ").strip()

            # Fetch the access token
            self.session.fetch_token(self.token_url, client_secret=self.client_secret, code=code)
            self._dump()
        else:
            # Refresh the token
            self.session.refresh_token(self.refresh_url, refresh_token=refresh_token, **credentials_data)
            self._dump()

    def _dump(self):
        """
        Save refresh token to client config
        """
        filename = os.path.expanduser('~/.mezzanine.cfg')
        parser = Parser()
        parser.add_section('general')
        parser.read(filename)
        parser.set('general', 'refresh_token', self.session.token['refresh_token'])
        with open(filename, 'w') as config_file:
            parser.write(config_file)

    @staticmethod
    def _json_serialize(obj):
        """
        Returns JSON serialization of an object
        """
        return json.dumps(obj)

    @staticmethod
    def _json_deserialize(string):
        """
        Returns dict deserialization of a JSON string
        """
        try:
            return json.loads(string)
        except ValueError:
            raise MezzanineValueError('Invalid API response.')

    def _url_joiner(self, *args):
        """
        Concatenate given endpoint resource with API URL
        """
        args = map(str, args)
        return '/'.join([self.api_url] + list(args))

    def _api_resource(self, method, resource, params=None, data=None):
        """
        Make an API request
        """
        url = self._url_joiner(*resource)
        response = self.session.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response

    def _get(self, resource, params=None):
        """
        Make a GET HTTP request
        """
        r = self._api_resource('GET', resource, params=params)
        item = self._json_deserialize(r.content.decode('utf-8'))
        return item

    def _post(self, resource, data, params=None):
        """
        Make a POST HTTP request
        """
        r = self._api_resource('POST', resource, data=self._json_serialize(data), params=params)
        item = self._json_deserialize(r.content.decode('utf-8'))
        return item

    def _put(self, resource, data, params=None):
        """
        Make a PUT HTTP request
        """
        r = self._api_resource('PUT', resource, data=self._json_serialize(data), params=params)
        item = self._json_deserialize(r.content.decode('utf-8'))
        return item


class Mezzanine(MezzanineCore):
    """
    The publicly accessible API client class
    """

    def __init__(self, credentials=None, api_url=None, version=None):
        super(Mezzanine, self).__init__(credentials, api_url, version)

    def get_post(self, item_id):
        """
        Get a published blog post
        :param item_id: id of blog post to retrieve
        :return: dict of specified blog post
        """
        return self._get(['posts', int(item_id)])

    def get_posts(self, offset=0, limit=10):
        """
        Get published blog posts
        :param offset: pagination offset
        :param limit: pagination limit
        :return: list of dicts for most recently published blog posts
        """
        return self._get(['posts?offset={}&limit={}'.format(int(offset), int(limit))])['results']

    def create_post(self, data):
        """
        Create a blog post
        :param data: blog post data in JSON format (requires 'title' and 'content')
        :return: deserialized API resource containing ID of the new blog post
        """
        return self._post(['posts'], data)

    def get_page(self, item_id):
        """
        Get a page
        :param item_id: id of page to retrieve
        :return: dict of specified page
        """
        return self._get(['pages', int(item_id)])

    def get_pages(self, offset=0, limit=10):
        """
        Get pages
        :param offset: pagination offset
        :param limit: pagination limit
        :return: list of dicts for pages
        """
        return self._get(['pages?offset={}&limit={}'.format(int(offset), int(limit))])['results']

    def get_user(self, item_id):
        """
        Get a user
        :param item_id: id of user to retrieve
        :return: dict of specified user
        """
        return self._get(['users', int(item_id)])

    def get_users(self, offset=0, limit=20):
        """
        Get users
        :param offset: pagination offset
        :param limit: pagination limit
        :return: list of dicts for users
        """
        return self._get(['users?offset={}&limit={}'.format(int(offset), int(limit))])['results']

    def get_category(self, item_id):
        """
        Get a category
        :param item_id: id of category to retrieve
        :return: dict of specified category
        """
        return self._get(['categories', int(item_id)])

    def get_categories(self, offset=0, limit=20):
        """
        Get categories
        :param offset: pagination offset
        :param limit: pagination limit
        :return: list of dicts for categories
        """
        return self._get(['categories?offset={}&limit={}'.format(int(offset), int(limit))])['results']

    def get_site(self):
        """
        Get site/app metadata
        :return: dict of site/app metadata
        """
        return self._get(['site'])
