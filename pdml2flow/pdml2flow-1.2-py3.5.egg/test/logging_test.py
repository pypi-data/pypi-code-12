#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .testcase import TestCase
import io

from pdml2flow.logging import *
from pdml2flow.conf import Conf

class TestLogging(TestCase):

    def test_debug(self):
        with io.StringIO() as out:
            Conf.OUT_DEBUG = out

            Conf.DEBUG = False
            debug('test')
            self.assertEqual(out.getvalue(), '')

            Conf.DEBUG = True
            debug('test')
            self.assertIn('test', out.getvalue())


    def test_warning(self):
        with io.StringIO() as out:
            Conf.OUT_WARNING = out

            warning('test')
            self.assertIn('test', out.getvalue())

if __name__ == '__main__':
    unittest.main()
