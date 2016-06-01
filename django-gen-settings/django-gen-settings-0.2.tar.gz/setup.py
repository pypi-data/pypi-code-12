from setuptools import setup, find_packages

setup(
  name = 'django-gen-settings',
  packages = find_packages(),
  version = '0.2',
  description = 'A settings mixin for django models',
  author = 'Paul Gueltekin',
  author_email = 'paul@gueltekin.at',
  url = 'https://github.com/paulgueltekin/django-gen-settings', 
  download_url = 'https://github.com/paulgueltekin/django-gen-settings/tarball/0.2',
  keywords = ['django', 'settings', 'model', 'mixin'],
  classifiers = [],
  install_requires=[
        'Django>=1.6',
    ],
)
