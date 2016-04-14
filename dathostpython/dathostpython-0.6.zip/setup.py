from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
  name = 'dathostpython',
  packages = ['dathostpython'],
  version = '0.6',
  description = 'A python wrapper for the Dathost API',
  long_description = long_description,
  author = 'Miles Budden',
  author_email = 'miles@budden.net',
  url = 'https://github.com/pbexe/dathost-python',
  keywords = ['dathost', 'hosting', 'wrapper'],
  classifiers = [],
)
