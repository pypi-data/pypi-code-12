from distutils.core import setup
setup(
  name = 'onestoppy',
  packages = ['onestoppy'], # this must be the same as the name above
  version = '0.2.1',
  description = 'A common helper library at 1-Stop',
  author = 'Mariusz Stankiewicz',
  author_email = 'mstankiewicz@1-stop.biz',
  install_requires=[
    'stompy',
    'sqlalchemy',
    'bottle',
    'pyconsul'
  ],
  keywords = ['onestoppy'], # arbitrary keywords
  classifiers = [],
)
