#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='rws',
      version='0.1.0',
      description='Ranking Web Server',
      author='Algorithm Ninja',
      author_email='algorithm@ninja',
      license='AGPL3',
      url='https://github.com/algorithm-ninja/rws',
      packages=find_packages(),
      install_requires=[
          'six',
          'gevent',
          'werkzeug'
      ],
      entry_points={
          'console_scripts': [
              'rws=cmsranking.RankingWebServer:main'
          ]
      })
