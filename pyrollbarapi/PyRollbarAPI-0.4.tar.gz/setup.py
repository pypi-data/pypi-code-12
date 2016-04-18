from distutils.core import setup

CURRENT_VERSION = '0.4'

setup(
  name = 'PyRollbarAPI',
  version = CURRENT_VERSION,
  py_modules = ['rollbarapi'],
  description = 'A class to make api calls to Rollbar',
  author = 'Snapsheet',
  author_email = 'technotifications@snapsheet.me',
  url = 'https://github.com/bodyshopbidsdotcom/PyRollbarAPI',
  download_url = 'https://github.com/bodyshopbidsdotcom/PyRollbarAPI/tarball/%s' % CURRENT_VERSION,
  keywords = ['api', 'gateway', 'http', 'REST'],
  install_requires = [
    'basegateway==0.10'
  ],
  classifiers = [
    "Topic :: Internet :: WWW/HTTP",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
)
