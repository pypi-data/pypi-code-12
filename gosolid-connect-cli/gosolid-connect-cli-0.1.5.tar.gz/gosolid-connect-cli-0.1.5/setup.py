#!/usr/bin/env python
from distutils.core import setup
setup(name='gosolid-connect-cli',
      version='0.1.5',
      description='CLI for interfacing with GoSolid projects',
      author='Andrew Venglar',
      author_email='andrew@gosolid.net',
      url='http://gosolid.net/',
      license='GPLv3',
      install_requires=['requests', 'gitpython'],
      package_dir={ '': 'cli' },
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
