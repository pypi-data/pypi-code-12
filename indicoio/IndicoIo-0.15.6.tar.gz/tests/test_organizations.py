import unittest

from indicoio import config
from indicoio import organizations


class Organizations(unittest.TestCase):
    def setUp(self):
        self.api_key = config.api_key
        config.url_protocol = "http"

        if not all(self.api_key):
            raise SkipTest

    def tearDown(self):
        config.url_protocol = "https"

    def test_organizations_v2(self):
        test_data = "A year ago, the New York Times published confidential comments about ISIS' ideology by Major General Michael K. Nagata, then U.S. Special Operations commander in the Middle East."
        response = organizations(test_data)
        self.assertTrue(isinstance(response, list))
        sorted_response = sorted(response, key=lambda x: x['confidence'], reverse=True)
        self.assertTrue('ISIS' in [result["text"] for result in sorted_response])

        test_data = [test_data] * 2
        response = organizations(test_data)
        self.assertTrue(isinstance(response, list))
        sorted_response = [sorted(arr, key=lambda x: x['confidence'], reverse=True) for arr in response]
        self.assertTrue('ISIS' in [result["text"] for result in sorted_response[0]])

    def test_organizations_v1(self):
        test_data = "A year ago, the New York Times published confidential comments about ISIS' ideology by Major General Michael K. Nagata, then U.S. Special Operations commander in the Middle East."
        response = organizations(test_data, version=1)
        self.assertTrue(isinstance(response, list))
        sorted_response = sorted(response, key=lambda x: x['confidence'], reverse=True)
        self.assertTrue('ISIS' in sorted_response[0]['text'])

        test_data = [test_data] * 2
        response = organizations(test_data, version=1)
        self.assertTrue(isinstance(response, list))
        sorted_response = [sorted(arr, key=lambda x: x['confidence'], reverse=True) for arr in response]
        self.assertTrue('ISIS' in sorted_response[0][0]['text'])
