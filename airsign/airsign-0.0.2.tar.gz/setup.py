#!/usr/bin/env python

from setuptools import setup

VERSION = '0.0.2'

setup(name='airsign',
      version=VERSION,
      description='Command line tool to interface with the BitShares network',
      long_description=open('README.md').read(),
      download_url='https://github.com/xeroc/airsign/tarball/' + VERSION,
      author='Fabian Schuh',
      author_email='<Fabian@BitShares.eu>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@BitShares.eu>',
      url='http://www.github.com/xeroc/airsign',
      keywords=['bitshares', 'library', 'api', 'rpc', 'cli'],
      packages=["airsign"],
      classifiers=['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   ],
      entry_points={
          'console_scripts': [
              'airsign = airsign.__main__:main',
          ],
      },
      install_requires=["graphenelib>0.3.9"],
      include_package_data=True,
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      )
