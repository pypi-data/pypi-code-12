import unittest

from indicoio import config
from indicoio import keywords


class KeywordsV2(unittest.TestCase):
    def setUp(self):
        self.api_key = config.api_key
        config.url_protocol = "http"

        if not all(self.api_key):
            raise SkipTest

    def tearDown(self):
        config.url_protocol = "https"

    def test_keywords_v2(self):
        test_data = "A working api is key to the success of our young company"
        response = keywords(test_data, version=2)
        self.assertTrue(isinstance(response, dict))
        self.assertTrue(all([key in test_data for key in response.keys()]))

    def test_batch_keywords_v2(self):
        test_data = ["A working api is key to the success of our young company"]
        response = keywords(test_data, version=2)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(all([key in test_data[0] for key in response[0].keys()]))
