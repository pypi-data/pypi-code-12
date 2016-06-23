import os, sys
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

try:
    from setuptools.command.test import test as TestCommand

    class PyTest(TestCommand):
        user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

        def initialize_options(self):
            TestCommand.initialize_options(self)
            self.pytest_args = []

        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            import pytest

            errno = pytest.main(self.pytest_args)
            sys.exit(errno)

except ImportError:
    PyTest = None

cmdclasses = {}
if PyTest:
    cmdclasses['test'] = PyTest

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = __import__('django_toolset').__version__

setup(
    name='django-toolset',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A set of helper functions and utilities for a Django application',
    download_url = 'https://github.com/codezeus/django-toolset/tarball/0.1.5',
    long_description=README,
    cmdclass=cmdclasses,
    url='https://github.com/codezeus/django-toolset',
    author='CodeZeus',
    maintainer='Dan Sackett',
    maintainer_email='danesackett@gmail.com',
    tests_require=['Django', 'pytest', 'pytest-cov', 'coverage', 'mock'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)
