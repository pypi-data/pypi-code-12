"""
magic_xxl
"""

from setuptools import setup, find_packages
from __about__ import *

setup(
    name=__title__,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email=__email__,
    description=__summary__,
    long_description=__doc__,
    url=__uri__,
    download_url='http://github.com/mardix/magic-xxl/tarball/master',
    py_modules=['magic_xxl'],
    keywords=["flask-magic",  "queue", "redis"],
    include_package_data=True,
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'boto==2.39.0',
        'redis==2.10.5',
        "redis-collections==0.1.7",
        "rollbar==0.12.1",
        "newrelic==2.64.0.48",
        "mutagen==1.31",
        "elasticsearch-dsl==0.0.11",
        "elasticsearch==2.2.0"
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
