from distutils.core import setup

setup(
  name = 'scrp',
  packages = ['scrp'],
  package_dir = {'scrp': 'scrp'},
  package_data = {'scrp': ['*']},
  version = '0.5',
  description = 'Methods for scraping the web',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/scrp',
  download_url = 'https://github.com/DanielJDufour/scrp',
  keywords = ['scraping'],
  classifiers = [],
)
