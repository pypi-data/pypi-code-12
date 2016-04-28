import chargehound
import requests_mock
import unittest2


class ChargehoundTest(unittest2.TestCase):

    @requests_mock.mock()
    def test_override_host(self, mock):
        orig_host = chargehound.host
        chargehound.host = 'test'
        mock.get('https://test/v1/disputes/dp_123',
                 json={'id': 'dp_123'})
        chargehound.Disputes.retrieve('dp_123')
        assert mock.called
        chargehound.host = orig_host
