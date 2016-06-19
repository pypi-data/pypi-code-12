#!/usr/bin/env python
from setuptools import setup, find_packages
setup(name='gosolid-connect-cli',
      version='0.1.8',
      description='CLI for interfacing with GoSolid projects',
      author='Andrew Venglar',
      author_email='andrew@gosolid.net',
      url='http://gosolid.net/',
      license='GPLv3',
      install_requires=['requests', 'gitpython'],
      packages=['cli'],
      package_dir={'cli': 'cli'},
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      scripts=[
         'connect',
      ],
      data_files=[],
)
