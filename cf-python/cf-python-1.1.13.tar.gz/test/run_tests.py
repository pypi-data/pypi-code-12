import unittest
import os
import netCDF4
import numpy
import datetime
import platform
import psutil
import sys
import cf

if platform.python_version() < '2.7.0':
    raise ValueError(
        "Bad python version for unit tests. Requires python <= 2.7.0. Got %s." %
        platform.python_version())

# Build the test suite from the tests found in the test files.
testsuite_setup = unittest.TestSuite()
testsuite_setup.addTests(unittest.TestLoader().discover('test', pattern='test_create_field.py'))

testsuite = unittest.TestSuite()
testsuite.addTests(unittest.TestLoader().discover('test', pattern='test_*.py'))

# Run the test suite.
def run_test_suite_setup(verbosity=2):
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(testsuite_setup)

# Run the test suite.
def run_test_suite(verbosity=2):
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(testsuite)

if __name__ == '__main__':
    original_chunksize = cf.CHUNKSIZE()
    print '--------------------'
    print 'CF-PYTHON TEST SUITE'
    print '--------------------'
    print 'Run date:', datetime.datetime.now()
    cf.ENVIRONMENT()
    print ''

    cf.CHUNKSIZE(original_chunksize)
    run_test_suite_setup()
    run_test_suite()

    cf.CHUNKSIZE(original_chunksize)
