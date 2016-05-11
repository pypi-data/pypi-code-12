import os
import unittest
from maintain.config import Config
from maintain.creators.license import LicenseCreator


class LicenseCreatorTests(unittest.TestCase):
    def test_license_name(self):
        self.assertEqual(LicenseCreator.name, 'license')

    def test_is_available(self):
        self.assertTrue(LicenseCreator.available)

    def test_validate_with_license(self):
        config = Config({'license': 'bsd'})
        creator = LicenseCreator(config, None)
        creator.validate()

    def test_validate_with_license_uppercase(self):
        config = Config({'license': 'BSD'})
        creator = LicenseCreator(config, None)
        creator.validate()

    def test_validate_with_unknown_license(self):
        config = Config({'license': 'kyle'})
        creator = LicenseCreator(config, None)
        with self.assertRaises(Exception):
            creator.validate()

    def test_validate_with_custom_license(self):
        config = Config({'license': {'file': __file__, 'type': 'Custom'}})
        creator = LicenseCreator(config, None)
        creator.validate()
        self.assertEqual(creator.license_name, 'Custom')
        self.assertEqual(creator.license_path, __file__)
