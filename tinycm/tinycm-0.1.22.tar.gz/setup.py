#!/usr/bin/env python3

from setuptools import setup, Command


def discover_and_run_tests():
    import os
    import sys
    import unittest

    # get setup.py directory
    setup_file = sys.modules['__main__'].__file__
    setup_dir = os.path.abspath(os.path.dirname(setup_file))

    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # use the basic test runner that outputs to sys.stderr
    test_runner = unittest.TextTestRunner()

    # automatically discover all tests
    # NOTE: only works for python 2.7 and later
    test_suite = test_loader.discover(setup_dir)

    # run the test suite
    result = test_runner.run(test_suite)
    if len(result.failures) + len(result.errors) > 0:
        exit(1)


class DiscoverTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        discover_and_run_tests()


setup(
        name='tinycm',
        version='0.1.22',
        packages=['tinycm', 'tinycm.definitions'],
        url='https://github.com/MartijnBraam/TinyCM',
        license='MIT',
        author='Martijn Braam',
        author_email='martijn@brixit.nl',
        description='Tiny Configuration Management tool',
        keywords=["configuration management", "puppet"],
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: MIT License"
        ],
        entry_points={
            'console_scripts': [
                'tinycm = tinycm.__main__:main'
            ]
        },
        install_requires=[
            'distro',
            'networkx',
            'requests',
            'ruamel.yaml',
            'tabulate',
            'boolexp',
            'pyparsing',
            'colorlog',
            'colorama'
        ],
        cmdclass={'test': DiscoverTest},
)
