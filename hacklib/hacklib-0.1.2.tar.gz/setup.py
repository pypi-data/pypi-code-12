from distutils.core import setup
setup(
  name = 'hacklib',
  packages = ['hacklib'], # this must be the same as the name above
  version = '0.1.2',
  description = 'Toolkit for hacking enthusiasts using Python.',
  author = 'Leon Li',
  author_email = 'leon@apolyse.com',
  url = 'https://github.com/leonli96/python-hacklib', # use the URL to the github repo
  download_url = 'https://github.com/leonli96/python-hacklib/tarball/0.1.2', # I'll explain this in a second
  keywords = ['hacking', 'python', 'network', 'security', 'port', 'scanning', 'login', 'cracking', 'dos',
              'proxy', 'scraping', 'ftp', 'sockets', 'scan'], # arbitrary keywords
  classifiers = [],
  install_requires = ['mechanize', 'beautifulsoup4']
)
