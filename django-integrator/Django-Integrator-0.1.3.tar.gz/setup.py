"""
PyPi Setup file.
"""
# pylint: disable=no-name-in-module, import-error
from distutils.core import setup
VERSION = '0.1.3'
BASE_URL = 'https://bitbucket.org/hellwig/django-integrator'

setup(
  name = 'Django-Integrator',
  packages = ['django_integrator'],
  version = VERSION,
  description = 'Tool for integrating compliant 3rd party django apps',
  author = 'Martin P. Hellwig',
  author_email = 'martin.hellwig@gmail.com',
  url = BASE_URL,
  download_url = BASE_URL + '/get/' + VERSION + '.zip',
  keywords = ['django'],
  license = 'BSD',
  classifiers = ['Programming Language :: Python :: 3',],
  install_requires = ['django'],
   entry_points = {
        'console_scripts':\
   ['mk_django_integrator_app=django_integrator.mk_django_integrator_app:main'],
    }
)

