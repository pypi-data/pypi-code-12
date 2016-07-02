# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 23:36:20 2015

@author: fly
"""


import os
from setuptools import setup, find_packages

def read_file(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(name='Memcached-cli',
      version='0.1-dev',
      platforms = ['Posix', 'Mac OS', 'Windows'], 
      description='A client cli for Memcached Server,which write by python.',
      long_description=read_file('README.rst'),
      author='fly',
      url='https://bitbucket.org/yafeile/memcached-cli',
      author_email='yafeile@sohu.com',
      install_requires = ['pymemcache'],
      classifiers=[
                  'License :: OSI Approved :: BSD License',
                  'Topic :: Database',
                  'Programming Language :: Python',
      ],
      entry_points={
        'console_scripts': ['memcached-cli = memcached_cli.main:main'],
      },
      packages=find_packages(), 
      keywords='memcached cli',
      license='BSD License'
      )
