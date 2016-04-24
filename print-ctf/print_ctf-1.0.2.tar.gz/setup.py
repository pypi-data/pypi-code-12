#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read().replace('\\_', '_')

setup(name='print_ctf',
      version='1.0.2',
      description='Print recent CTF contests sourced by CTFTime.org',
      long_description=long_description,
      author='deko2369',
      author_email='deko2369@gmail.com',
      url='https://github.com/deko2369',
      packages=find_packages(),
      install_requires=['icalendar', 'pytz', 'requests'],
      entry_points={
          'console_scripts': [
              'print_ctf = print_ctf:__main',
          ]
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Other Audience',
          'License :: Public Domain',
          'Topic :: Utilities',
          'Programming Language :: Python',
      ],
     )

