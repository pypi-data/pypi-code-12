"""
 harvest.py

 Author: Jonathan Hosmer (forked from https://github.com/lionheart/python-harvest.git)
 Date: Sat Jan 31 12:17:16 2015

"""

import requests
from base64 import b64encode as enc64
try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode

from .constants import *


class HarvestError(Exception):
    pass

class HarvestRestClient(object):

    _uri = None
    _authorize_data = {}
    _authorize_url = None
    _oauth2 = False
    _email = None
    _password = None
    _content_type = None
    _headers = {}

    _errors = {
        'invalid_uri': 'Invalid harvest uri "{0}".',
        'request_failed': 'Harvest request failed. Status code: {0}. Error: {1}',
        'not_oauth2': 'Oauth2 is not available with basic authentication'
    }

    def __init__(self, uri, content_type=None, **kwargs):
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError(self._errors.get('invalid_uri').format(uri))
        self.uri = uri

        if not content_type:
            self.content_type = HTTPContentType.JSON
        else:
            self.content_type = content_type

        #Reset the headers on every initialization
        self.headers = {
            HTTPHeader.ACCEPT: self.content_type
        }
        
        self.oauth2 = bool(kwargs.get(OauthKey.CLIENT_ID))
        if self.oauth2:
            self.authorize_data = {
                OauthKey.CLIENT_ID: kwargs.get(OauthKey.CLIENT_ID),
                OauthKey.REDIRECT_URI: kwargs.get(OauthKey.REDIRECT_URI),
                OauthKey.RESPONSE_TYPE: OauthValue.CODE
            }
            self.authorize_url = '%s/%s' %(self.uri, HARVEST_OAUTH_AUTHORIZE_PATH)
            
        else:
            self.email    = kwargs.get(BasicKey.EMAIL)
            self.password = kwargs.get(BasicKey.PASSWORD)
            auth_string = '{self.email}:{self.password}'.format(self=self)
            try:
                #python3
                auth_string = enc64(auth_string.encode('utf-8')).decode()
            except TypeError:
                #python2
                auth_string = enc64(auth_string)
            self.set_header(HTTPHeader.AUTH, HTTPHeader.BASIC_AUTH_FORMAT.format(auth_string))
            

        
    def set_header(self, key, value):
        self._headers.update({
            key: value
        })

    def raise_if_not_oauth(self):
        if not self.oauth2:
            raise HarvestError(self._errors.get('not_oauth2'))

    def get_tokens(self, code, secret):
        self.raise_if_not_oauth()
        data = {
            OauthKey.CODE: code,
            OauthKey.CLIENT_ID: self.authorize_data.get(OauthKey.CLIENT_ID),
            OauthKey.CLIENT_SECRET: secret,
            OauthKey.REDIRECT_URI: self.authorize_data.get('redirect_uri'),
            OauthKey.GRANT_TYPE: OauthValue.AUTH_CODE
        }
        self.set_header(HTTPHeader.CONTENT_TYPE, HTTPContentType.FORM_ENCODED)
        rsp = self._post(HARVEST_OAUTH_TOKEN_PATH, params=data) #Data must be in query parameters
        self.reset_content_type() #Reset this content type
        return (rsp.get(OauthKey.ACCESS_TOKEN), rsp.get(OauthKey.REFRESH_TOKEN))

    def refresh_tokens(self, token, secret):
        self.raise_if_not_oauth()
        data = {
            OauthKey.CLIENT_ID: self.authorize_data.get(OauthKey.CLIENT_ID),
            OauthKey.CLIENT_SECRET: secret,
            OauthKey.REFRESH_TOKEN: token,
            OauthKey.GRANT_TYPE: OauthValue.REFRESH_TOKEN
        }
        self.set_form_encoded_type()
        rsp = self._post(HARVEST_OAUTH_TOKEN_PATH, params=data)
        self.reset_content_type()
        return (rsp.get(OauthKey.ACCESS_TOKEN), rsp.get(OauthKey.REFRESH_TOKEN))
        
    def reset_content_type(self):
        self.set_header(HTTPHeader.CONTENT_TYPE, self.content_type)

    def set_form_encoded_type(self):
        self.set_header(HTTPHeader.CONTENT_TYPE, HTTPContentType.FORM_ENCODED)

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, val):
        self._content_type = val

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        self._uri = value.rstrip('/')

    @property
    def token_url(self):
        return '%s/%s' %(self.uri, HARVEST_OAUTH_TOKEN_PATH)

    @property
    def authorize_url(self):
        return self._authorize_url

    @authorize_url.setter
    def authorize_url(self, value):
        self._authorize_url = '%s?%s' %(value, urlencode(self.authorize_data))

    @property
    def authorize_data(self):
        return self._authorize_data
    
    @authorize_data.setter
    def authorize_data(self, val):
        self._authorize_data = val

    @property
    def oauth2(self):
        return self._oauth2

    @oauth2.setter
    def oauth2(self, val):
        self._oauth2 = val

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, val):
        self._email = val.strip()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        self._password = val

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, val):
        self._headers = val
    

    @property
    def status(self):
        return status()

    ## Accounts

    def who_am_i(self, params=None):
        return self._get('/account/who_am_i', params=params)

    ## Projects

    def projects(self, params=None):
        return self._get('/projects', params=params)

    def get_project(self, project_id, params=None):
        return self._get('/projects/{0}'.format(project_id), params=params)

    def create_project(self, params=None, **kwargs):
        return self._post('/projects', data=kwargs, params=params)

    def update_project(self, project_id, params=None, **kwargs):
        url = '/projects/{0}'.format(project_id)
        return self._put(url, data=kwargs, params=params)

    def toggle_project_active(self, project_id, params=None,):
        return self._put('/projects/{0}/toggle'.format(project_id), params=params)

    def delete_project(self, project_id, params=None):
        return self._delete('/projects/{0}'.format(project_id), params=params)

    ## Client Contacts

    def contacts(self, updated_since=None, params=None):
        url = '/contacts'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def get_contact(self, contact_id, params=None):
        return self._get('/contacts/{0}'.format(contact_id))

    def create_contact(self, new_contact_id, fname, lname, params=None, **kwargs):
        url  = '/contacts/{0}'.format(new_contact_id)
        kwargs.update({'first-name':fname, 'last-name':lname})
        return self._post(url, data=kwargs)

    def client_contacts(self, client_id, updated_since=None, params=None):
        url = '/clients/{0}/contacts'.format(client_id)
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def update_contact(self, contact_id, params=None, **kwargs):
        url = '/contacts/{0}'.format(contact_id)
        return self._put(url, data=kwargs)

    def delete_contact(self, contact_id, params=None):
        return self._delete('/contacts/{0}'.format(contact_id))

    ## Clients

    def clients(self, updated_since=None, params=None):
        url = '/clients'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url, params=params)

    def get_client(self, client_id, params=None):
        return self._get('/clients/{0}'.format(client_id), params=params)

    def create_client(self, new_client_id, name, params=None, **kwargs):
        url  = '/clients/{0}'.format(new_client_id)
        kwargs.update({'name':name})
        return self._post(url, data=kwargs, params=params)

    def update_client(self, client_id, params=None, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return self._put(url, data=kwargs, params=params)

    def toggle_client_active(self, client_id, params=None):
        return self._get('/clients/{0}/toggle'.format(client_id), params=params)

    def delete_client(self, client_id, params=None):
        return self._delete('/clients/{0}'.format(client_id), params=params)

    ## Tasks
    def tasks(self, params=None):
        """Retrieves all tasks from Harvest.
        Will filter by updated since if provided in the params.
        """
        url = '/tasks'
        return self._get(url, params=params)

    ## Expense Categories

    @property
    def expense_categories(self):
        return self._get('/expense_categories')

    def create_expense_category(self, new_expense_category_id, **kwargs):
        return self._post('/expense_categories/{0}'.format(new_expense_category_id), data=kwargs)

    def update_expense_category(self, expense_category_id, **kwargs):
        return self._put('/expense_categories/{0}'.format(expense_category_id), data=kwargs)

    def get_expense_category(self, expense_category_id):
        return self._get('/expense_categories/{0}'.format(expense_category_id))

    def delete_expense_category(self, expense_category_id):
        return self._delete('/expense_categories/{0}'.format(expense_category_id))

    def toggle_expense_category_active(self, expense_category_id):
        return self._get('/expense_categories/{0}/toggle'.format(expense_category_id))

    ## Time Tracking

    def today(self, params=None):
        return self._get('/daily', params=params)

    def get_day(self, day_of_the_year=1, year=2012, params=None):
        return self._get('/daily/{0}/{1}'.format(day_of_the_year, year), params=params)

    def get_entry(self, entry_id):
        return self._get('/daily/show/{0}'.format(entry_id), params=None)

    def toggle_timer(self, entry_id):
        return self._get('/daily/timer/{0}'.format(entry_id))

    def add(self, data, params=None):
        return self._post('/daily/add', data, params=params)

    def delete(self, entry_id):
        return self._delete('/daily/delete/{0}'.format(entry_id))

    def update(self, entry_id, data):
        return self._post('/daily/update/{0}'.format(entry_id), data)

    def _get(self, path='/', data=None, params=None):
        return self._request('GET', path, data, params)
    def _post(self, path='/', data=None, params=None):
        return self._request('POST', path, data, params=params)
    def _put(self, path='/', data=None, params=None):
        return self._request('PUT', path, data, params=params)
    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)
    def _request(self, method='GET', path='/', data=None, params=None):
        url = '{self.uri}{path}'.format(self=self, path=path)
        kwargs = {
            'method'  : method,
            'url'     : url,
            'headers' : self.headers,
            'data'    : data,
            'params'  : params
        }
        if not self.oauth2 and 'Authorization' not in self.headers:
            kwargs['auth'] = (self.email, self.password)

        try:
            resp = requests.request(**kwargs)
            if self.response_is_successful(resp.status_code):
                if 'DELETE' not in method:
                    return resp.json()
                return resp
            else:
                raise HarvestError(self._errors.get('request_failed').format(resp.status_code, resp.json()))
        except Exception as e:
            raise HarvestError(e)

    def response_is_successful(self, status_code):
        return 200 <= status_code < 300


def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get('status', {})
    except:
        status = {}
    return status
