#!/usr/bin/env python
"""
    Setup file for pycreate
"""

import sys
from setuptools import setup

def setup_package():
    setup(
        setup_requires=['pbr>=1.9', 'setuptools>=17.1', 'pytest-runner>=2.0,<3dev'],
        tests_require=['pytest'],
        pbr=True
    )

if __name__ == "__main__":
    setup_package()
