#!/usr/bin/env python

from setuptools import setup

setup(name='WDK',
      version='1.0.1b1',
      description='Python API for D-Link WDK',
      author='Martin Sundhaug',
      author_email='martinsundhaug@gmail.com',
      url='https://github.com/sundhaug92/dlink-wdk',
      py_modules=['wdk'],
      license='MIT',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2 :: Only',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Security',
          'Topic :: Software Development :: Embedded Systems',
          'Topic :: Software Development :: Libraries'
      ],
      keywords='dlink dir100 wdk web cliget api'
)
