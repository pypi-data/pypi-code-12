"""
distutilazy.tests.test_pyinstaller
----------------------------------

Tests for distutilazy.pyinstaller module.

:license: MIT, see LICENSE for more details.
"""

import sys
from os.path import dirname
from unittest import TestCase, main
import re

here = dirname(__file__)
sys.path.insert(0, dirname(here))
sys.path.insert(0, here)

from distutilazy.pyinstaller import BdistPyInstaller, CleanAll
from distutils.dist import Distribution


class TestPyinstaller(TestCase):

    def test_finalize_opts(self):
        dist = Distribution()
        pi = BdistPyInstaller(dist)
        pi.target = "fake.py"
        pi.finalize_options()
        self.assertTrue( re.match(".+", pi.name) )
        self.assertTrue(pi.pyinstaller_opts)

    def test_clean_all(self):
        dist = Distribution()
        cl = CleanAll(dist)
        cl.finalize_options()
        paths = cl.get_extra_paths()
        self.assertTrue(paths)
        spec = paths.pop()
        self.assertTrue( re.match("\S+\.spec", spec) )

if __name__ == "__main__":
    main()