# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio user management and authentication."""

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'pytest-flask>=0.10.0',
    'selenium>=2.48.0',
    'Flask-CeleryExt>=0.1.0',
    'Flask-CLI>=0.2.1',
    'Flask-Mail>=0.9.1',
]

extras_require = {
    ':python_version=="2.7"': ['ipaddr>=2.1.11'],
    'celery': [
        'celery>=3.1.0',
    ],
    'docs': [
        'Sphinx>=1.3',
    ],
    'mysql': [
        'invenio-db[mysql]>=1.0.0a6',
    ],
    'postgresql': [
        'invenio-db[postgresql]>=1.0.0a6',
    ],
    'sqlite': [
        'invenio-db>=1.0.0a6',
    ],
    'admin': [
        'invenio-admin>=1.0.0a2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':':
        continue
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
]

install_requires = [
    'Flask-BabelEx>=0.9.2',
    'Flask-Login>=0.3.0',
    'Flask-Menu>=0.4.0',
    'Flask-Security>=1.7.5',
    'Flask-KVSession>=0.6.1',
    'SQLAlchemy-Utils[ipaddress]>=0.31.0',
    'redis>=2.10.5',
]

packages = find_packages()


class PyTest(TestCommand):
    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        if hasattr(self, '_test_args'):
            self.test_suite = ''
        else:
            self.test_args = []
            self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_accounts', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-accounts',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio accounts',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    url='https://github.com/inveniosoftware/invenio-accounts',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_admin.views': [
            'invenio_accounts_user = invenio_accounts.admin:user_adminview',
            'invenio_accounts_role = invenio_accounts.admin:role_adminview',
        ],
        'invenio_base.apps': [
            'invenio_accounts = invenio_accounts:InvenioAccounts',
        ],
        'invenio_base.api_apps': [
            'invenio_accounts = invenio_accounts:InvenioAccounts',
        ],
        'invenio_base.blueprints': [
            'invenio_accounts = invenio_accounts.views:blueprint',
        ],
        'invenio_db.models': [
            'invenio_accounts = invenio_accounts.models',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_accounts',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
    cmdclass={'test': PyTest},
)
