#!/usr/bin/env python3

from setuptools import setup

VERSION = '0.2.2.2'

setup(name='gnusrss',
      version=VERSION,
      description='Post feeds to GNU Social.',
      long_description=open('README.rst', encoding='utf-8').read(),
      author='drymer',
      author_email='drymer@autistici.org',
      url='http://daemons.cf/cgit/gnusrss/about/',
      download_url='http://daemons.cf/cgit/gnusrss/snapshot/gnusrss-' + VERSION + '.tar.gz',
      scripts=['gnusrss.py'],
      license="GPLv3",
      install_requires=[
          "feedparser>=5.0",
          "pycurl>=7.0",
          ],
      classifiers=["Development Status :: 4 - Beta",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4",
                   "Operating System :: OS Independent",
                   "Operating System :: POSIX",
                   "Intended Audience :: End Users/Desktop"]
      )
