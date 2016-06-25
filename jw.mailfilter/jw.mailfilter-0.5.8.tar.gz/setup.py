#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name="jw.mailfilter",
    version="0.5.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'setuptools',
        'jw.util',
        'gevent',
        'dnspython',
        'imapclient',
        'pyzor',
        'beautifulsoup4',
        'future',
        'sphinxjp.themes.dotted',
    ],
    package_data={
        '': ['*.rst', '*.txt']
    },
    entry_points={
        'console_scripts': [
            'mailfilter = mailfilter.main:Main'
        ],
        'jw.mailfilter.filter': [
            'all = mailfilter.filters:All',
            'rbl = mailfilter.filters:RblFilter',
            'pyzor = mailfilter.filters:PyzorFilter',
            'url = mailfilter.filters:UrlFilter',
            'body = mailfilter.filters:BodyFilter',
            'header = mailfilter.filters:HeaderFilter',
        ],
        'jw.mailfilter.action': [
            'copy-to = mailfilter.action:CopyToAction',
            'move-to = mailfilter.action:MoveToAction',
            'delete = mailfilter.action:DeleteAction',
            'set-flag = mailfilter.action:SetFlagAction',
            'clear-flag = mailfilter.action:ClearFlagAction',
            'report-pyzor = mailfilter.action:PyzorReportAction',
            'report-badips = mailfilter.action:ReportBadipsAction',
            'forward-to = mailfilter.action:ForwardAction',
            'stop = mailfilter.action:StopAction',
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
    author="Johnny Wezel",
    author_email="dev-jay@wezel.name",
    description="IMAP mail filter",
    long_description='IMAP mail filter',
    license="GPL",
    platforms='POSIX',
    keywords="mail, imap, filter, spam",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    url="https://pypi.python.org/pypi/jw.mailfilter"
)
import setuptools.command.install

