from __future__ import print_function

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

version = '1.0.1'

if sys.version_info <= (2, 5):
    error = "ERROR: closedown requires Python Version 2.6 or above...exiting."
    print(error, file=sys.stderr)
    sys.exit(1)

setup(name = "closedown",
      version = version,
      description = "CloseDown API SDK Library",
      long_description = "CloseDown API SDK.",
      author = "Kim SeongJun",
      author_email = "pallet027@gmail.com",
      url = "https://github.com/linkhub-sdk/closedown.py",
      download_url = "https://github.com/linkhub-sdk/closedown.py/archive/"+version+".tar.gz",
      packages = ["closedown"],
      install_requires=[
          'linkhub',
      ],
      license = "MIT",
      platforms = "Posix; MacOS X; Windows",
      classifiers = ["Development Status :: 5 - Production/Stable",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                     "Topic :: Internet",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.3",
                     "Programming Language :: Python :: 3.4"]
      )
