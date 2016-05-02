#!/usr/bin/env python
import os
import urllib

from setuptools import setup, find_packages, Command

import django_sec

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_reqs(*fns):
    lst = []
    for fn in fns:
        for package in open(os.path.join(CURRENT_DIR, fn)).readlines():
            package = package.strip()
            if not package:
                continue
            lst.append(package.strip())
    return lst
    
setup(
    name = "django-sec",
    version = django_sec.__version__,
    packages = find_packages(),
#    package_data = {
#        'django_sec': [
#            'templates/*.*',
#            'templates/*/*.*',
#            'templates/*/*/*.*',
#            'static/*.*',
#            'static/*/*.*',
#            'static/*/*/*.*',
#        ],
#    },
    author = "Chris Spencer",
    author_email = "chrisspen@gmail.com",
    description = "Parse XBRL filings from the SEC's EDGAR in Python",
    license = "LGPL",
    url = "https://github.com/chrisspen/django-sec",
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
    ],
    zip_safe = False,
    install_requires=get_reqs('pip-requirements-min-django.txt', 'pip-requirements.txt'),
    tests_require=get_reqs('pip-requirements-test.txt'),
)
