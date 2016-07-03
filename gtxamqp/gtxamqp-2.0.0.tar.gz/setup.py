import io
import os
import sys
from gtxamqp import __version__

from setuptools import setup
from setuptools.command.test import test as TestCommand


here = os.path.abspath(os.path.dirname(__file__))

class PyTest(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='gtxamqp',
    version=__version__,
    url='http://github.com/devsenexx/gtxamqp',
    license='MIT License',
    author='Alexey Vishnevsky & Oded Lazar',
    tests_require=['pytest'],
    install_requires=['txAMQP>=0.6.2'],
    cmdclass={'test': PyTest},
    author_email='aliowka@gmail.com | odedlaz@gmail.com',
    description='AMQP Reconnecting Client for Twisted',
    packages=['gtxamqp'],
    package_data={'gtxamqp': ['amqp0-8.stripped.rabbitmq.xml']},
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
