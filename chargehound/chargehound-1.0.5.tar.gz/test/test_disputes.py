import chargehound
import requests_mock
import unittest2
from chargehound.version import VERSION


get_headers = {
    'accept': 'application/json',
    'authorization': 'Basic QVBJX0tFWTo=',
    'user-agent': 'Chargehound/v1 PythonBindings/' + VERSION
}

post_headers = {
    'accept': 'application/json',
    'authorization': 'Basic QVBJX0tFWTo=',
    'content-type': 'application/json',
    'user-agent': 'Chargehound/v1 PythonBindings/' + VERSION
}


class DisputeTest(unittest2.TestCase):

    def setUp(self):
        super(DisputeTest, self).setUp()
        chargehound.api_key = 'API_KEY'

    @requests_mock.mock()
    def test_retrieve_dispute(self, mock):
        mock.get('https://api.chargehound.com/v1/disputes/dp_123',
                 status_code=200,
                 request_headers=get_headers,
                 json={'id': 'dp_123'})
        chargehound.Disputes.retrieve('dp_123')
        assert mock.called

    @requests_mock.mock()
    def test_list_all_disputes(self, mock):
        mock.get('https://api.chargehound.com/v1/disputes',
                 status_code=200,
                 request_headers=get_headers,
                 json={'data': [{'id': 'dp_123'}]})
        chargehound.Disputes.list()
        assert mock.called

    @requests_mock.mock()
    def test_submit_dispute(self, mock):
        mock.post('https://api.chargehound.com/v1/disputes/dp_123/submit',
                  status_code=201,
                  json={'id': 'dp_123'})
        chargehound.Disputes.submit('dp_123',
                                    fields={'customer_name': 'Susie'})
        assert mock.request_history[0].body == \
            '{"fields": {"customer_name": "Susie"}}'
        assert mock.called

    @requests_mock.mock()
    def test_update_dispute(self, mock):
        mock.post('https://api.chargehound.com/v1/disputes/dp_123',
                  status_code=200,
                  json={'id': 'dp_123'})
        chargehound.Disputes.update('dp_123',
                                    fields={'customer_name': 'Susie'})
        assert mock.request_history[0].body == \
            '{"fields": {"customer_name": "Susie"}}'
        assert mock.called
