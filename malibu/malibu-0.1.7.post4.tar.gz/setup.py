# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import os
import sys

sys.path.insert(0, os.path.abspath('src'))

import malibu

setup(
    name='malibu',
    version=malibu.__version__,
    description="maiome library of utilities - rev %s" % (malibu.__release__),

    url="https://glow.dev.ramcloud.io/maiome/malibu",
    author="Sean Johnson",
    author_email="sean.johnson@maio.me",

    license="Unlicense",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=find_packages('src'),
    package_dir={
        '': 'src'
    },
    install_requires=[
        'dill'
    ],
    include_package_data=True,
    exclude_package_data={
        '': ['README.md'],
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'coverage',
        'requests',
    ],
    zip_safe=True
)
