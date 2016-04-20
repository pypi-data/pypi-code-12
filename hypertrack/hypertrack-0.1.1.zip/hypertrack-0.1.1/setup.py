import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hypertrack'))
from hypertrack.version import VERSION

with open('LONG_DESCRIPTION.rst') as f:
    long_description = f.read()

setup(
    name = "hypertrack", # pip install hypertrack
    description = "api wrapper for hypertrack.io",
    long_description=long_description,
    version = VERSION,
    author = 'HyperTrack',
    author_email = "devops@hypertrack.io",
    url = 'http://github.com/hypertrack/hypertrack-python/',
    license = 'MIT',
    install_requires = ["requests >= 0.8.8", ],
    py_modules = ["hypertrack"],
    zip_safe = True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
