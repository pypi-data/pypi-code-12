from distutils.core import setup
setup(
  name = 'onestoppy',
  packages = ['onestoppy'], # this must be the same as the name above
  version = '0.1.7',
  description = 'A common helper library at 1-Stop',
  author = 'Mariusz Stankiewicz',
  author_email = 'mstankiewicz@1-stop.biz',
  install_requires=[
    'requests',
    'sqlalchemy',
    'bottle',
    'pyconsul'
  ],
  keywords = ['onestop'], # arbitrary keywords
  classifiers = [],
)
