#!/usr/bin/env python
'''
Created on 2015/11/17

:author: hubo
'''
try:
    import ez_setup
    ez_setup.use_setuptools()
except:
    pass
from setuptools import setup, find_packages

VERSION = '0.1.5'

setup(name='vlcpssh',
      version=VERSION,
      description='Integrate paramiko into ssh',
      author='Hu Bo',
      author_email='hubo1016@126.com',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      url='http://github.com/hubo1016/vlcp-ssh',
      keywords=['VLCP', 'paramiko'],
      test_suite = 'tests',
      use_2to3=False,
      install_requires = ["vlcp","paramiko"],
      packages=find_packages(exclude=("tests","tests.*","misc","misc.*")))
