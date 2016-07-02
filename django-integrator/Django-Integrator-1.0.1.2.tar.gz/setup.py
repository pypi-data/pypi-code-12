"""
PyPi Setup file.
"""
import os
# pylint: disable=no-name-in-module, import-error
from setuptools import setup

NAME = 'Django-Integrator'
DESCRIPTION = 'Create and use django-integrator compliant applications.'
VERSION = '1.0.1.2'
LICENSE = 'BSD'
AUTHOR = 'Martin P. Hellwig'
AUTHOR_EMAIL = 'martin.hellwig@gmail.com'
#
URL_MAIN = "https://bitbucket.org/hellwig/" + NAME + '/'
DOWNLOAD_ID = os.environ.get('CI_COMMIT_ID', VERSION)
URL_DOWNLOAD = URL_MAIN + 'get/' + DOWNLOAD_ID + '.zip'
#
PACKAGES = ['django_integrator', 'django_integrator_script']
PACKAGE_DATA  = {'django_integrator_script': ['templates/*.txt']}
SCRIPT = 'django-integrator-create='\
         'django_integrator_script.make_application:main'
KEYWORDS = [
    'django',
    ]
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    ]
REQUIREMENTS = [
    'Django',
    'pip',
    ]


################################################################################

KWARGS = {
    'name':NAME, 'packages':PACKAGES, 'version':VERSION,
    'description':DESCRIPTION, 'author':AUTHOR, 'author_email':AUTHOR_EMAIL,
    'url':URL_MAIN, 'download_url':URL_DOWNLOAD, 'keywords':KEYWORDS,
    'license':LICENSE, 'classifiers':CLASSIFIERS,
    'install_requires':REQUIREMENTS, 'package_data':PACKAGE_DATA,
    'entry_points':{'console_scripts':[SCRIPT]},}

setup(**KWARGS)
