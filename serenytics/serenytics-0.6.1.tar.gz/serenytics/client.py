import cPickle
import json
from base64 import b64encode

from .source import DataSource, UnknownDataSource
from .helpers import SerenyticsException, make_request, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_429_TOO_MANY_REQUESTS
from . import settings


def _init_headers(api_key):
    token = 'token:' + api_key
    return {
        'Authorization': 'Basic ' + b64encode(token),
        'Content-type': 'application/json'
    }


class Client(object):
    """
    Main wrapper around Serenytics API
    """

    def __init__(self, api_key, script_id=None):
        """
        :param api_key: API key (get on https://app.serenytics.com/studio/account)
        :param script_id: [Optional] id of the script on Serenytics website, required if you plan on storing and
        retrieving data associated to the script between executions.
        """
        self._script_id = script_id
        self._headers = _init_headers(api_key)

    def get_data_source_by_uuid(self, uuid):
        """
        Fetch a data source by uuid

        :param uuid: string
        :return: DataSource instance
        """
        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + uuid
        response = make_request('get', data_source_url,
                                custom_exceptions={HTTP_404_NOT_FOUND: UnknownDataSource(uuid)},
                                headers=self._headers)
        return DataSource(response.json(), self._headers)

    def get_data_source_by_name(self, name):
        """
        Fetch a data source by its name.

        :param name: string
        :return: DataSource instance if there is exactly one data source with this name. Returns None if there isn't
        any data source with this name. Raise a SerenyticsException if there are multiple data sources with this name.
        """
        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source'
        params = {'q': json.dumps({'filters': [{'name': 'name', 'op': 'eq', 'val': name}]})}
        response = make_request('get', data_source_url,
                                params=params,
                                headers=self._headers)

        sources = response.json()

        if sources['num_results'] == 1:
            source = sources['objects'][0]
            return DataSource(source, self._headers)

        elif sources['num_results'] > 1:
            raise SerenyticsException('There are multiple sources named "%s". Please rename other sources.' % name)

        return None

    def get_or_create_storage_data_source_by_name(self, name):
        """
        Retrieve the data source whose name is `name` or create a new one.

        :param name: string
        :return: DataSource instance
        """
        data_source = self.get_data_source_by_name(name)

        if data_source is not None:
            return data_source

        data_source_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source'
        response = make_request('post', data_source_url,
                                data=json.dumps({'name': name, 'type': 'Storage', 'jsonContent': {}}),
                                expected_status_code=HTTP_201_CREATED,
                                headers=self._headers)
        source = response.json()
        return DataSource(source, self._headers)

    @property
    def _script_storage_url(self):
        if self._script_id is None:
            raise SerenyticsException('You must initialize the client with the script_id before using script storage')
        return settings.SERENYTICS_API_DOMAIN + '/api/script/' + self._script_id + '/storage'

    def store_script_data(self, data):
        """
        Store script data to be retrieved during next execution of the script.

        :param data: any python object that can be pickled
        """
        make_request('put', self._script_storage_url, data=cPickle.dumps(data), headers=self._headers)

    def retrieve_script_data(self):
        """
        Retrieve script data saved in previous script execution.
        """
        response = make_request('get', self._script_storage_url, headers=self._headers)
        try:
            return cPickle.loads(response._content)
        except Exception:
            return None

    @property
    def script_args(self):
        """
        Get args passed to the script
        """
        try:
            with open('params.json') as params_file:
                params = json.load(params_file)
            return params
        except IOError:
            return None

    def send_email(self, subject, recipients, html, web_app_uuid=None):
        """
        Send an email through Serenytics API

        :param subject: String containing the email subject
        :param recipients: List of strings containing recipients email addresses
        :param html: String containing HTML body
        :param web_app_uuid: (Optional) String uuid of webapp to include as a PDF attachment in the email
        """
        make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/email',
                     headers=self._headers,
                     custom_exceptions={HTTP_429_TOO_MANY_REQUESTS: TooManyEmailsSent()},
                     data=json.dumps({
                         'subject': subject,
                         'recipients': recipients,
                         'html': html,
                         'web_app_uuid': web_app_uuid
                     }),
                     timeout=10*60)  # generate report can be long


class TooManyEmailsSent(SerenyticsException):
    """Exception raised when more emails are sent than authorized by the current rate limit"""
