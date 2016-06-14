"""
PyPi Setup file.
"""
# pylint: disable=no-name-in-module, import-error
from setuptools import setup
VERSION = '1.0.0.3'
BASE_URL = 'https://bitbucket.org/hellwig/django-integrator'
SCRIPT = 'django-integrator-create='\
         'django_integrator_script.make_application:main'

setup(
  name = 'Django-Integrator',
  packages = ['django_integrator', 'django_integrator_script'],
  version = VERSION,
  description = 'Create and use django-integrator compliant applications.',
  author = 'Martin P. Hellwig',
  author_email = 'martin.hellwig@gmail.com',
  url = BASE_URL,
  download_url = BASE_URL + '/get/' + VERSION + '.zip',
  keywords = ['django'],
  license = 'BSD',
  classifiers = ['Programming Language :: Python :: 3',],
  install_requires = ['django', 'pip'],
  entry_points = {'console_scripts':[SCRIPT]},
  package_data={'django_integrator_script': ['templates/*.txt']},
)

