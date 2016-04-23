#!/usr/bin/env python

from setuptools import setup

setup(author='Peter Marsh',
      author_email='pete.d.marsh@gmail.com',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development'
      ],
      entry_points = {'console_scripts': ['lolcommitmsg=lolcommitmsg:main']},
      include_package_data=True,
      description='Make your commit messages lovely',
      download_url='https://github.com/petedmarsh/lolcommitmsg/tarball/0.1.0',
      long_description=open('README.rst').read(),
      name='lolcommitmsg',
      package_data={'': ['LICENSE', 'README.rst']},
      py_modules = ['lolcat', 'lolcommitmsg'],
      url='https://github.com/petedmarsh/lolcommitmsg',
      version='0.1.0')
