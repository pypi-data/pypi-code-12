import os
import unittest
from maintain.config import Config
from maintain.creators import LicenseCreator, PythonCreator


class PythonCreatorTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual(PythonCreator.name, 'python')

    def test_depends_on_license(self):
        self.assertEqual(PythonCreator.dependencies(), [LicenseCreator])
