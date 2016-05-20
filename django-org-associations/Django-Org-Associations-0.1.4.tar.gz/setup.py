"""
PyPi Setup file.
"""
# pylint: disable=no-name-in-module, import-error
from setuptools import setup, find_packages
VERSION = '0.1.4'
BASE_URL = 'https://github.com/blancltd/django-associations'
DOWNLOAD = 'https://github.com/blancltd/django-associations/archive/master.zip'

DEPENDENCIES = [
   'django',
   'django-integrator>=0.1.0',
]

CLASSIFIERS = [
   'Programming Language :: Python :: 3',
   'Environment :: Web Environment',
   'Framework :: Django',
   'Framework :: Django :: 1.9',
   'License :: OSI Approved :: BSD License',
   'Operating System :: OS Independent',
]

setup(
   name = 'Django-Org-Associations',
   packages = find_packages(),
   include_package_data=True,
   version = VERSION,
   description = 'Django Organisation/Member associations',
   author = 'Blanc Limited',
   author_email = 'studio@blanc.tld.uk',
   maintainer = 'Martin P. Hellwig',
   maintainer_email = 'martin.hellwig@gmail.com',
   platforms=['any'],
   url = BASE_URL,
   download_url = DOWNLOAD,
   keywords = ['django'],
   license = 'BSD',
   install_requires = DEPENDENCIES,
   classifiers = CLASSIFIERS,
)

