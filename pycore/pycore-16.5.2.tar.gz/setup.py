from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'pycore',
  packages = find_packages(),
  version = '16.05.02',
  description = 'CoreCluster API Library',
  author = 'Maciej & Marta Nabozny',
  author_email = 'mn@mnabozny.pl',
  url = 'http://cloudover.org/pycore/',
  download_url = 'https://github.com/cloudOver/PyCloud/archive/master.zip',
  keywords = ['corecluster', 'overcluster', 'cloudover', 'cloud'],
  classifiers = [],
  install_requires = ['requests', 'pytest', 'pytest-cov']
)
