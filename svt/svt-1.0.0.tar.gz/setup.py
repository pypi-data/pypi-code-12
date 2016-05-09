#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import python libs
import os
import sys
import shutil

if 'USE_SETUPTOOLS' in os.environ or 'setuptools' in sys.modules:
    from setuptools import setup
else:
    from distutils.core import setup
    from distutils.core import Command

NAME = 'svt'
DESC = ('Standalone port of the salt-vt terminal emulation system')

# Version info -- read without importing
_locals = {}
with open('svt/version.py') as fp:
    exec(fp.read(), None, _locals)
VERSION = _locals['version']


class Clean(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for subdir in ('svt'):
            for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), subdir)):
                for dir_ in dirs:
                    if dir_ == '__pycache__':
                        shutil.rmtree(os.path.join(root, dir_))


setup(name=NAME,
      author='Thomas S Hatch',
      author_email='thatch45@gmail.com',
      version=VERSION,
      description=DESC,
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          ],
      packages=[
          'svt',
          ],
      cmdclass={'clean': Clean},
      )
