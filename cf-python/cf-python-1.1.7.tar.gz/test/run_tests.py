import unittest
import os
import netCDF4
import numpy
import datetime
import platform
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
    print 'Run date:'              , datetime.datetime.now()
    print 'HDF5 lib version:'      , netCDF4. __hdf5libversion__
    print 'netcdf lib version:'    , netCDF4.__netcdf4libversion__
    print 'python version:'        , platform.python_version()
    print 'netcdf4-python version:', netCDF4.__version__
    print 'numpy version:'         , numpy.__version__
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    print ''

    cf.CHUNKSIZE(original_chunksize)
    run_test_suite_setup()
    run_test_suite()


    print ''
    print '--------'
    print 'Versions'
    print '--------'
    print 'HDF5 lib version:'      , netCDF4. __hdf5libversion__
    print 'netcdf lib version:'    , netCDF4.__netcdf4libversion__
    print 'python version:'        , platform.python_version()
    print 'netcdf4-python version:', netCDF4.__version__
    print 'numpy version:'         , numpy.__version__
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    cf.CHUNKSIZE(original_chunksize)
