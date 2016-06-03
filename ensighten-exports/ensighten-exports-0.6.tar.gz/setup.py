from __future__ import absolute_import
from setuptools import setup, find_packages

setup(name='ensighten-exports',
  version='0.6',
  packages=find_packages(),
  description = 'Ensighten exports command line interface',
  include_package_data=True,
  url='https://bitbucket.org/ensighten-ondemand/dataintelligence-exports-cli',
  classifiers=[
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    'Programming Language :: Python :: 2.7',
],
  install_requires=['click==6.3',
    'urllib3>=1.14',
    'tqdm==4.7.1',
    'six >= 1.9',
    'python-dateutil',
    'requests==2.10.0',
    'PyYAML==3.11',
    'ndg-httpsclient>=0.4.0'],
  entry_points={
    'console_scripts': [
      'exports = di_export_cli.cli:cli'
    ]
  })
