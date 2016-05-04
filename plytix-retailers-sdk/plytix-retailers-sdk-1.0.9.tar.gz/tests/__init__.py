import unittest
from plytix.retailers.client import PlytixRetailersClient


class RetailersTestCase(unittest.TestCase):
    def setUp(self):
        self.api_key = '555ef5401d5ca71fe489e791'
        self.api_pwd = '555ef5401d5ca71fe489e792'
        self.client = PlytixRetailersClient(self.api_key, self.api_pwd)

    def tearDown(self):
        pass

from .brands import *
from .data import *
from .folders import *
from .globals import *
from .products import *
from .sites import *