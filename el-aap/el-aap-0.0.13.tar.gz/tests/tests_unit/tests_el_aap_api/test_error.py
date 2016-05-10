__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import patch

from el_aap_api.errors import *


class TestError(TestCase):
    def setUp(self):
        response_patcher = patch('el_aap_api.errors.response', autospec=False)
        self.response = response_patcher.start()

    def test_error_catcher_base_error(self):
        @error_catcher
        def testfunc():
            raise BaseError(200, 815, 'blarg')

        result = testfunc()

        self.assertEqual(200, self.response.status)
        self.assertEqual({'code': 815, 'msg': 'blarg'}, result)

