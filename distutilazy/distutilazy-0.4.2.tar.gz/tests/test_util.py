"""
distutilazy.tests.test_util
-----------------

Test distutilazy.util module.
"""

from __future__ import absolute_import

import sys
from os.path import dirname, realpath
from unittest import TestCase, main

here = dirname(__file__)
sys.path.insert(0, dirname(here))
sys.path.insert(0, here)

from distutilazy import util

if __file__.endswith('$py.class'):
    __file__ = __file__[:-9] + '.py'
elif __file__.endswith('.pyc'):
    __file__ = __file__[:-1]

class TestUtil(TestCase):

    def test_util_find_files(self):
        me = realpath(__file__)
        files = util.find_files(here, "test_util.py*")
        self.assertIn(me, files)
        files = util.find_files(here, "not_existing_file.py")
        self.assertEqual(files, [])

    def test_util_find_directories(self):
        found = util.find_directories(dirname(here), "tes*")
        self.assertIn(here, found)
        found = util.find_directories(here, "not_existing_dir")
        self.assertEqual(found, [])
