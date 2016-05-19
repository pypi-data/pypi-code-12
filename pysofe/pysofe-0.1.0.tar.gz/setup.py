#!/usr/bin/python2

import codecs
import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# define some helper functions
# ----------------------------
here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """
    Build an absolute path from parts and return the contents of the
    resulting file assuming utf-8 encoding.
    """

    with codecs.open(os.path.join(here, *parts), 'rb', 'utf-8') as f:
        return f.read()

meta_path = os.path.join("pysofe", "__init__.py")
meta_file = read(meta_path)

def find_meta(meta):
    """
    Extract __*meta*__ from the meta data file.
    """

    meta_match = re.search(pattern=r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
                           string=meta_file,
                           flags=re.M)

    if meta_match:
        return meta_match.group(1)

    raise RuntimeError("Unable to find __{meta}__ string!".format(meta=meta))

# set meta data
# -------------
meta_data = dict(author = "Andreas Kunze",
                 author_email = "andreas.kunze@mailbox.tu-dresden.de",
                 classifiers = ['Environment :: Console',
                                'Development Status :: 4 - Beta',
                                'Intended Audience :: Science/Research',
                                'Intended Audience :: Developers',
                                'License :: OSI Approved :: BSD License',
                                'Natural Language :: English',
                                'Operating System :: OS Independent',
                                'Programming Language :: Python',
                                'Topic :: Scientific/Engineering',
                                'Topic :: Software Development :: Libraries :: Python Modules'],
                 cmdclass = {'test': PyTest},
                 description = "FEM library for solving PDEs in 1D, 2D and 3D",
                 extras_require = {'testing': ['pytest'],
                                   'visualization' : ['matplotlib>=1.5.1']},
                 install_requires = ['numpy>=1.10.4',
                                     'scipy>=0.16.1',
                                     'matplotlib>=1.5.0',
                                     'ipython'],
                 license = "BSD",
                 long_description = read("README.rst"),
                 name = "pysofe",
                 packages = find_packages(),
                 platforms = 'any',
                 tests_require = ['pytest'],
                 url = "https://github.com/pysofe/pysofe",
                 version = find_meta('version'),
                 zip_safe=False)

if __name__ == "__main__":
    setup(**meta_data)
