"""
PyPi Setup file.
"""
# pylint: disable=no-name-in-module, import-error
from distutils.core import setup

setup(
  name = 'Django-Integrator',
  packages = ['django_integrator'],
  version = '0.1.0',
  description = 'Tool for integrating compliant 3rd party django apps',
  author = 'Martin P. Hellwig',
  author_email = 'martin.hellwig@gmail.com',
  url = 'https://bitbucket.org/hellwig/django-integrator',
  download_url = 'https://bitbucket.org/hellwig/django-integrator/get/0.1.0.zip',
  keywords = ['django'],
  classifiers = [],
)

