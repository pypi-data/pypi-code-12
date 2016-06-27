from codecs import open
from os import path

from setuptools import setup, find_packages

from xstatic_release import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xstatic-release',
    version=__version__,
    description='Tool to help OpenStack Horizon developers package xstatic',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xstatic-release=xstatic_release:main',
        ],
    }
)
