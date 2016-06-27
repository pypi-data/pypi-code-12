# python setup.py register -r pypitest
# python setup.py sdist upload -r pypitest
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi

from distutils.core import setup
setup(
  name = 'rypy',
  packages = ['rypy'],
  version = '0.0.5',
  description = 'RYan\'s PYthon tools',
  author = 'Ryan Smith',
  author_email = 'rms1000watt@gmail.com',
  url = 'https://github.com/rms1000watt/rypy',
  download_url = 'https://github.com/rms1000watt/rypy/tarball/0.1', 
  keywords = ['logging', 'tools'], 
  classifiers = [],
)