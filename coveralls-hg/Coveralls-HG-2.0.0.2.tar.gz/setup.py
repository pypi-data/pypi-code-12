"""
PyPi Setup file.
"""
import os
# pylint: disable=no-name-in-module, import-error
from setuptools import setup

NAME = 'Coveralls-HG'
DESCRIPTION = 'Coveralls API for: Python 3+, Coverage & Mercurial.'
VERSION = '2.0.0.2'
LICENSE = 'BSD'
AUTHOR = 'Martin P. Hellwig'
AUTHOR_EMAIL = 'martin.hellwig@gmail.com'
#
URL_MAIN = "https://bitbucket.org/hellwig/" + NAME + '/'
DOWNLOAD_ID = os.environ.get('CI_COMMIT_ID', VERSION)
URL_DOWNLOAD = URL_MAIN + 'get/' + DOWNLOAD_ID + '.zip'
#
PACKAGES = ['coveralls_hg']
PACKAGE_DATA  = {}
SCRIPTS = []
KEYWORDS = [
    'Coveralls',
    'Codeship',
    'BitBucket'
    ]
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    ]
REQUIREMENTS = [
    'setuptools',
    'requests',
    'coverage',
    ]


################################################################################

KWARGS = {
    'name':NAME, 'packages':PACKAGES, 'version':VERSION,
    'description':DESCRIPTION, 'author':AUTHOR, 'author_email':AUTHOR_EMAIL,
    'url':URL_MAIN, 'download_url':URL_DOWNLOAD, 'keywords':KEYWORDS,
    'license':LICENSE, 'classifiers':CLASSIFIERS,
    'install_requires':REQUIREMENTS, 'package_data':PACKAGE_DATA,
    'entry_points':{'console_scripts':SCRIPTS},}

setup(**KWARGS)
