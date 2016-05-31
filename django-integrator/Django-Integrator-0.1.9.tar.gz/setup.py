"""
PyPi Setup file.
"""
# pylint: disable=no-name-in-module, import-error
from distutils.core import setup
VERSION = '0.1.9'
BASE_URL = 'https://bitbucket.org/hellwig/django-integrator'
SCRIPT = 'mk_django_integrator_app='\
         'django_integrator_script.make_application:main'

setup(
  name = 'Django-Integrator',
  packages = ['django_integrator', 'django_integrator_script'],
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
  entry_points = {'console_scripts':[SCRIPT]},
  package_data={'django_integrator_script': ['templates/*.txt']},
)

