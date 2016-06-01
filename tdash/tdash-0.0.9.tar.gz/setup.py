from setuptools import setup
setup(
  name = 'tdash',
  packages = ['tdash'], # this must be the same as the name above
  version = '0.0.9',
  description = 'Collection of utils inspired by underscore and lodash. No guarantees that I will not change this on a whim',
  author = 'Andrew Jefferson',
  author_email = 'andyj.trinity@gmail.com',
  url = 'https://github.com/eastlondoner/tdash', # use the URL to the github repo
  download_url = 'https://github.com/eastlondoner/tdash/tarball/0.0.9',
  keywords = [], # arbitrary keywords
  classifiers = [],
  install_requires=[
      'pydash'
  ]
)
