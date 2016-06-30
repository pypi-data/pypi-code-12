"""
Tests for the codamag package.
"""

import unittest
from pkg_resources import resource_filename

def run():
    loader = unittest.TestLoader()
    test_dir = resource_filename('codamag', 'tests')
    tests = loader.discover(test_dir)
    test_runner = unittest.runner.TextTestRunner()
    test_runner.run(tests)

if __name__ == '__main__':
    run()
