#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_qpic_script
----------------------------------

Tests for `qpic` module.
compare -metric mae 2Bitcomp.png output.png diff.png 
0 (0) if files are the same
"""

from __future__ import print_function

import collections
import os
import os.path
import unittest

try:
    # Python2
    from itertools import izip_longest as zip_longest
except ImportError:
    # Python3
    from itertools import zip_longest

class CommandLineTestCase(unittest.TestCase):
    '''
    '''
    @classmethod
    def setUpClass(cls):
        parser = create_parser()
        cls.parser = parser

class QpicTestCase(CommandLineTestCase):
    pass

if __name__ == '__main__':
    sys.exit(unittest.main())
