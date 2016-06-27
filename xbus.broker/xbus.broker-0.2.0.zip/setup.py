# -*- encoding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

with open(os.path.join(here, 'CONTRIBUTORS.rst')) as f:
    CONTRIBUTORS = f.read()

# TODO Specific version of SQLAlchemy because the latest fails when using a
# custom UUID type registered by xbus.broker ("can't adapt type 'UUID'").

# TODO Specific versions of aiopg, msgpack-python, psycopg2, pyzmq because the
# latest fail when the broker wants to know whether a list is empty; it
# receives the '{None}' string instead of an empty list.
# Code ref: xbus/broker/core/back/rpc.py:298.
# As the problem has not yet been identified, the 4 packages are frozen.

requirements = [
    'aiopg==0.5.1',
    'aioredis',
    'aiozmq',
    'hiredis',
    'msgpack-python==0.4.3',
    'psycopg2==2.5.4',
    'pyzmq==14.4.1',
    'SQLAlchemy==0.9.8',
]

setup(
    name='xbus.broker',
    version='0.2.0',
    description='Xbus Broker written in Python3',
    long_description="{}\n{}\n{}".format(README, CONTRIBUTORS, CHANGES),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    author='Florent Aide',
    author_email='florent.aide@xcg-consulting.fr',
    url='https://bitbucket.org/xcg/xbus.broker',
    keywords='xbus',
    packages=find_packages(exclude=['tests', ]),
    namespace_packages=['xbus'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=[
        "nose",
        "coverage",
    ],
    test_suite='nose.collector',
    entry_points={
        "console_scripts": [
            'setup_xbusbroker = xbus.broker.cli:setup_xbusbroker',
            'start_xbusbroker = xbus.broker.cli:start_server',
        ],
    },
)
