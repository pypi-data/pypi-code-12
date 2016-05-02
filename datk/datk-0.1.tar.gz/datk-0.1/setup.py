from distutils.core import setup
version = 0.1
setup(
  name = 'datk',
  packages = ['datk'], # this must be the same as the name above
  version = str(version),
  description = 'Distributed Algorithms Toolkit for Python',
  author = 'Amin Manna',
  author_email = 'manna@mit.edu',
  url = 'https://github.com/amin10/datk',
  download_url = 'https://github.com/amin10/datk/tarball/'+str(version),
  keywords = ['distributed', 'algorithms', 'toolkit', 'simulator'],
  classifiers = [],
)