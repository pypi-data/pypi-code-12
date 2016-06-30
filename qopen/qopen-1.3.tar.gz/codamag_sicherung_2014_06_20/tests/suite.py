"""
Submodule fetching all test suites and returning a merged test suite.
"""
import unittest
import test_core
import test_rt


def suite():
    return unittest.TestSuite([test_core.suite(),
                               test_rt.suite()])


def main():
    unittest.TextTestRunner().run(suite())

if __name__ == '__main__':
    main()
