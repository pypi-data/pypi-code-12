# python rypy/rypy.py 
# python setup.py register -r pypitest
# python setup.py sdist upload -r pypitest
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi
# sudo pip install --upgrade rypy

from distutils.core import setup
setup(
  name = 'rypy',
  packages = ['rypy'],
  version = '0.0.10',
  description = 'RYans PYthon tools',
  author = 'Ryan Smith',
  author_email = 'rms1000watt@gmail.com',
  url = 'https://github.com/rms1000watt/rypy',
  keywords = ['logging', 'tools'], 
  classifiers = [],
)