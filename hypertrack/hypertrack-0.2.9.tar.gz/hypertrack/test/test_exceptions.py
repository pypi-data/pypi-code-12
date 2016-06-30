# -*- coding: utf-8 -*-
import sys
import unittest2

from hypertrack.exceptions import HyperTrackException


class ExceptionsTests(unittest2.TestCase):
    '''
    Test custom exceptions
    '''
    def test_formatting(self):
        excp = HyperTrackException(u'café', '{"body":"json"}')

        if sys.version_info > (3, 0):
            assert str(excp) == u'café'
        else:
            assert str(excp) == 'caf\xc3\xa9'
            assert unicode(excp) == u'café'
