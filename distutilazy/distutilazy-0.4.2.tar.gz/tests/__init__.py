"""
distutilazy.tests
-----------------

Tests for distutilazy

:license: MIT, see LICENSE for more details.
"""

from os.path import basename, splitext, join, dirname
from glob import glob

test_modules = [
    splitext(basename(filename))[0] for filename in glob(
        join(dirname(__file__), 'test*.py'))
    ]
test_modules.sort()

__all__ = test_modules