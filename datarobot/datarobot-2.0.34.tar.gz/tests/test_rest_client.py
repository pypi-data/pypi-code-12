import mock
import responses

from datarobot.rest import RequestContext
from datarobot.errors import AppPlatformError
from datarobot.client import get_client
from .utils import SDKTestcase


class TestBuildRequestWithFile(SDKTestcase):

    def test_file_doesnt_exist(self):
        client = get_client()
        with self.assertRaises(AppPlatformError):
            client.build_request_with_file(
                'PUT', 'http://host-name/', 'meh.csv', file_path='meh.csv')

    def test_non_string_content(self):
        client = get_client()
        with self.assertRaises(AssertionError):
            client.build_request_with_file(
                'PUT', 'http://host-name/', 'meh.csv', content=1234)


class TestRequestContext(SDKTestcase):

    @responses.activate
    @mock.patch('datarobot.rest')
    def test_exception_handling_during_request(self, rest):
        url = 'http://host-name/'
        request_context = RequestContext('GET', url, headers={})
        responses.add(
            responses.GET,
            url,
            status=500,
            body='',
        )
        with self.assertRaisesRegexp(AppPlatformError, 'server error:'):
            request_context.send_request()
