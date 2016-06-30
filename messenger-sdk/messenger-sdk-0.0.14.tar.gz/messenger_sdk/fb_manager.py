from tornado import gen, httpclient

from messenger_sdk.config import Config
from messenger_sdk.fb_response import FbResponse
from messenger_sdk.api_client import ApiClient


class FbManager:
    def __init__(self, api_client: ApiClient, config: Config):
        self._api_client = api_client
        self._fb_api_url = config.get_parameter('facebook', 'FB_API')
        self._fb_graph_url = config.get_parameter('facebook', 'FB_GRAPH')
        self._fb_token = config.get_parameter('facebook', 'FB_TOKEN')

    @staticmethod
    def get_input_entries(entry):
        entries = None
        if entry.get('object') == 'page' and entry.get('entry') and isinstance(entry.get('entry'), list) and len(
                entry.get('entry')) > 0:
            for entry in entry.get('entry'):
                if entry and entry.get('messaging') and isinstance(
                        entry.get('messaging'), list) and len(entry.get('messaging')) > 0:
                    entries = entry.get('messaging')

        return entries

    @gen.coroutine
    def send(self, response: FbResponse, url=None):
        if not isinstance(response, FbResponse):
            raise TypeError('Invalid response class. Expected {expected}, {given} given.'.format(
                expected=FbResponse.__name__,
                given=type(response).__name__))
        for template in response.templates:
            try:
                if url is None:
                    url = self._fb_api_url
                yield self._api_client.async_request(url=url, http_method='POST', body=template)
            except httpclient.HTTPError as e:
                e.message = 'FB error: {message}'.format(message=e.message)
                raise e

    @gen.coroutine
    def get_user_info(self, user_id):
        headers = {'Authorization': 'Bearer {token}'.format(token=self._fb_token)}
        url = '{base_url}/{user_id}'.format(base_url=self._fb_graph_url, user_id=user_id)
        try:
            response = yield self._api_client.async_request(url=url, headers=headers)
            return response
        except httpclient.HTTPError as e:
            e.message = 'Unable to get user info: {message}'.format(message=e.message)
            raise e
