#!/usr/bin/env python

#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


"""Setup script for Robot's DatabaseLibrary distributions"""

from distutils.core import setup

import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), 'src'))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup
execfile(join(dirname(__file__), 'src', 'DatabaseLibrary', 'version.py'))

def main():
    setup(name         = 'robotframework-databaseslibrary',
          version      = VERSION,
          description  = 'Database utility library for Robot Framework',
          author       = 'qitaos',
          author_email = 'qitaos@gmail.com',
          url          = 'https://github.com/qitaos/Robotframework-Database-Library/',
          package_dir  = { '' : 'src'},
          packages     = ['DatabaseLibrary'],
          package_data={'DatabaseLibrary': ['VERSION']},
          requires     = ['robotframework']
          )
        

if __name__ == "__main__":
    main()
