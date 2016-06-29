import unittest

from indicoio import config
from indicoio import places


class Places(unittest.TestCase):
    def setUp(self):
        self.api_key = config.api_key
        config.url_protocol = "http"

        if not all(self.api_key):
            raise SkipTest

    def tearDown(self):
        config.url_protocol = "https"

    def test_places_v2(self):
        test_data = "Lets all go to Virginia beach before it gets too cold to wander outside."
        response = places(test_data)
        self.assertTrue(isinstance(response, list))
        sorted_response = sorted(response, key=lambda x: x['confidence'], reverse=True)
        self.assertTrue('Virginia' in sorted_response[0]['text'])

        test_data = [test_data] * 2
        response = places(test_data)
        self.assertTrue(isinstance(response, list))
        sorted_response = [sorted(arr, key=lambda x: x['confidence'], reverse=True) for arr in response]
        self.assertTrue('Virginia' in sorted_response[0][0]['text'])

    def test_places_v1(self):
        test_data = "Lets all go to Virginia beach before it gets too cold to wander outside."
        response = places(test_data, version=1)
        self.assertTrue(isinstance(response, list))
        sorted_response = sorted(response, key=lambda x: x['confidence'], reverse=True)
        self.assertTrue('Virginia' in sorted_response[0]['text'])

        test_data = [test_data] * 2
        response = places(test_data, version = 1)
        self.assertTrue(isinstance(response, list))
        sorted_response = [sorted(arr, key=lambda x: x['confidence'], reverse=True) for arr in response]
        self.assertTrue('Virginia' in sorted_response[0][0]['text'])
