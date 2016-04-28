'''
yamlfred:

Licensed under CC0.
'''
from setuptools import setup, find_packages

import sys

version = "0.3.3"

if sys.version_info < (2, 6) or (3, 0) <= sys.version_info < (3, 3):
    print('ERROR: yamlfred requires at least Python 2.7 or 3.3 to run.')
    sys.exit(1)
requires = ['PyYAML', 'six']

if sys.version_info < (3, 3):
    requires.append('ChainMap')

setup(name="yamlfred",
      version=version,
      description="manage Alfred workflow via yaml templates",
      long_description=open("README.rst").read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 1 - Planning',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
          'Topic :: Utilities',
      ],
      keywords="", # Separate with spaces
      author="Akihiro Uchida",
      author_email="uchida@turbare.net",
      url="https://github.com/uchida/yamlfred",
      license="CC0",
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'testfixtures'],
      entry_points={
          'console_scripts': ['yamlfred=yamlfred:main']
      }
)
