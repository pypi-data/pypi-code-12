import pytest
from datarobot.client import get_client
from .utils import SDKTestcase


class TestBuildRequestWithFile(SDKTestcase):

    def test_file_doesnt_exist(self):
        client = get_client()
        with self.assertRaises(ValueError):
            client.build_request_with_file(
                'PUT', 'http://host-name/', 'meh.csv', file_path='meh.csv')

    def test_non_string_content(self):
        client = get_client()
        with self.assertRaises(AssertionError):
            client.build_request_with_file(
                'PUT', 'http://host-name/', 'meh.csv', content=1234)


def test_strip_endpoint(client):
    url = 'https://host_name.com/the/url/I/want/'
    stripped = client.strip_endpoint(url)
    assert stripped == 'the/url/I/want/'


def test_strip_endpoint_invalid_url(client):
    url = 'http://localhost/api/v2/wrong/prefix/on/this/url'
    with pytest.raises(ValueError):
        client.strip_endpoint(url)
