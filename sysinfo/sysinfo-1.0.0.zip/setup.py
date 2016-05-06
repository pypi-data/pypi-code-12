# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import codecs
import os
import re
from setuptools import setup


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


required = ['psutil']

LONG_DESCRIPTION = """
**sysinfo** is a Python package that provides information about the system.

- Operatin system
- Processor
- Installed memory
- Available memory
- System architecture
- Hostname
- Username
- Python version
"""

setup(
    name='sysinfo',
    packages=['sysinfo'],
    version=find_version('sysinfo', 'sysinfo.py'),
    description='Bootstrap for console and file logging configuration',
    install_requires=required,
    long_description=LONG_DESCRIPTION,
    author='Rafael Santos',
    author_email='rstogo@outlook.com',
    url='https://github.com/rtogo/sysinfo',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
)
