#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest, os

from indicoio import config
from indicoio import image_recognition

DIR = os.path.dirname(os.path.realpath(__file__))
class ImageRecognitionTest(unittest.TestCase):
    def setUp(self):
        self.api_key = config.api_key

    def test_single_image_recognition(self):
        test_data = os.path.normpath(os.path.join(DIR, "data", "fear.png"))
        response = image_recognition(test_data, api_key = self.api_key, top_n=3)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIsInstance(list(response.values())[0], float)

    def test_batch_image_recognition(self):
        test_data = os.path.normpath(os.path.join(DIR, "data", "fear.png"))
        response = image_recognition([test_data, test_data], api_key = self.api_key, top_n=3)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0], dict)
        self.assertEqual(len(response[0]), 3)
        self.assertIsInstance(list(response[0].values())[0], float)

    def test_expected_response(self):
        test_data = os.path.normpath(os.path.join(DIR, "data", "keyboard.jpg"))
        response = image_recognition(test_data, api_key = self.api_key, top_n=3)
        assert "space bar" in response.keys()

if __name__ == "__main__":
    unittest.main()
