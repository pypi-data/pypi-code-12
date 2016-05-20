#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='resyndicator',
    version='0.1.2',
    author='Denis Drescher',
    author_email='denis.drescher+resyndicator@claviger.net',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'utilofies',
        'twython',
        'requests',
        'python-dateutil',
        'feedparser',
        'SQLAlchemy',
        'awesome-slugify',
        'beautifulsoup4',
        'psycopg2',
        'readability-lxml',
        'xmltodict',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'resyndicator = resyndicator.console:run'
        ]
    }
)
