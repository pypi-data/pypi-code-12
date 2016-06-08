from distutils.core import setup
setup(
  name = 'hello_pip_goran',
  packages = ['hello_pip_goran'], # this must be the same as the name above
  version = '0.3',
  description = 'A random test lib',
  author = 'Goran Iliev',
  author_email = 'goraniliev93@gmail.com',
  url = 'https://github.com/goraniliev/HelloPip', # use the URL to the github repo
  download_url = 'https://github.com/goraniliev/HelloPip/tarball/0.3', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)