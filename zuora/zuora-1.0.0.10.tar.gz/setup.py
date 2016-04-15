from setuptools import (
        find_packages,
        setup,
)
from setuptools.command.test import test as TestCommand

import sys
import subprocess



class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='zuora',
    version='1.0.0.10',
    author='MapMyFitness',
    author_email='brandon.fredericks@mapmyfitness.com',
    url='http://github.com/clearcare/python-zuora',
    description='Zuora client library.',
    tests_require=['pytest', 'mock'],
    cmdclass={'test': PyTest},
    packages=find_packages(),
    package_data = {
            '': ['*.wsdl'],
    },
    install_requires=[
        'suds==0.4',
        'requests',
    ],
    zip_safe=False,
)
