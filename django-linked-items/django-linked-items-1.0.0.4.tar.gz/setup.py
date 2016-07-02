"""
PyPi Setup file.
"""
import os
# pylint: disable=no-name-in-module, import-error
from setuptools import setup, find_packages

NAME = 'django-linked-items'
DESCRIPTION = 'Linked Items'
VERSION = '1.0.0.4'
AUTHOR = 'Martin P. Hellwig'
AUTHOR_EMAIL = 'martin.hellwig@gmail.com'
URL_MAIN = "https://bitbucket.org/hellwig/" + NAME + '/'
DOWNLOAD_ID = os.environ.get('CI_COMMIT_ID', VERSION)
URL_DOWNLOAD = URL_MAIN + 'get/' + DOWNLOAD_ID + '.zip'

KEYWORDS = [
    'django',
    'django-integrator'
    ]

CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    ]

REQUIREMENTS = [
    'Django',
    'django-integrator',
    ]

LICENSE = 'BSD'

################################################################################

KWARGS = {
    'name':NAME, 'packages':find_packages(), 'version':VERSION,
    'description':DESCRIPTION, 'author':AUTHOR, 'author_email':AUTHOR_EMAIL,
    'url':URL_MAIN, 'download_url':URL_DOWNLOAD, 'keywords':KEYWORDS,
    'license':LICENSE, 'classifiers':CLASSIFIERS,
    'install_requires':REQUIREMENTS}

setup(**KWARGS)
