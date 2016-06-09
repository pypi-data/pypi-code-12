#!/usr/bin/env python
import unittest
import psychic_disco
import example_package  # noqa


class TestApi(unittest.TestCase):
    def test_entry_points(self):
        expected = "psychic_disco.tests.example_package.handler"
        entry_point = psychic_disco.entry_points()[0]
        actual = entry_point.full_name
        self.assertEqual(expected, actual)

    def test_api_calls(self):
        expected = "psychic_disco.tests.example_package.hova"
        api_object = psychic_disco.Api["GET /that/dirt/off/your/shoulder"]
        actual = api_object.full_name
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
