import unittest

from psychic_disco.rest_api import RestApi


class TestRestApi(unittest.TestCase):
    def test_find(self):
        api = RestApi.find("dummy-manager")
        self.assertEqual("123apiid", api.aws_id)
        self.assertTrue(api.exists_in_aws)
        self.assertEqual(2, len(api.resources))
        self.assertIn('/', api.resources)
        self.assertIn('/dummies', api.resources)

    def test_find_caches(self):
        api1 = RestApi.find("dummy-manager")
        api2 = RestApi.find("dummy-manager")
        self.assertEqual(api1, api2)

    def test_find_creates_nonexistent(self):
        api1 = RestApi.find("dummy-manager-nonexistent")
        self.assertIsNotNone(api1)
