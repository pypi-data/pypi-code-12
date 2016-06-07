# coding:utf8
import sys
from setuptools import setup, find_packages
import os
import codecs
import re

here = os.path.dirname(os.path.abspath(__file__))

if sys.version_info[:2] < (3, 5) and sys.argv[-1] == 'install':
    sys.exit('stack requires python 3.5 or higher')


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='stack-scaffold',
    version=find_version('__init__.py'),
    url='http://python-stack.readthedocs.io',
    description='`stack` is a Python version of [stack](http://docs.haskellstack.org/en/stable/README/),',
    author='Ryan Kung',
    py_modules=find_packages(exclude=['tests']),
    author_email='ryankung@ieee.org',
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs']),
    package_dir={'': '.'},
    tests_require=['nose'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    include_package_data=True,
    entry_points={'console_scripts': [
        'scaffold = scaffold.main:main',
    ]},

)
