#!/usr/bin/env python

import sys

from setuptools import setup


PY3 = (sys.version_info[0] == 3)

try:
    import unittest.mock    # noqa
except ImportError:
    requires_mock = ['mock']
else:
    requires_mock = []

try:
    import unittest2  # noqa
except ImportError:
    test_loader = 'unittest:TestLoader'
else:
    test_loader = 'unittest2:TestLoader'


setup(
    name='mockldap',
    version='0.2.7',
    description=u"A simple mock implementation of python-ldap.",
    long_description=open('README').read(),
    url='http://bitbucket.org/psagers/mockldap/',
    author='Peter Sagerson',
    author_email='psagers.pypi@ignorare.net',
    license='BSD',
    packages=['mockldap'],
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
    keywords=['mock', 'ldap'],
    install_requires=[
        'pyldap' if PY3 else 'python-ldap',
        'funcparserlib==0.3.6',
    ] + requires_mock,
    extras_require={
    },
    setup_requires=[
        'setuptools>=0.6c11',
    ],
    test_loader=test_loader,
    test_suite='mockldap.tests',
)
