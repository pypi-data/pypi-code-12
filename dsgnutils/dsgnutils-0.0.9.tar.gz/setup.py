'''
Copyright 2015 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import re
from setuptools import setup
from setuptools import find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def parseReqs():
    ret=None
    with open('requirements.txt','r') as f:
        ret=f.read()
    ret=ret.split('\n')
    ret=[x for x in ret if not re.match(r'^#',x)]
    ret=[x for x in ret if x]
    return ret

setup(
    name = "dsgnutils",
    version = "0.0.9",
    author = "define()",
    author_email = "define2.0x@gmail.com",
    description = ("several general purpose pythons I use all the time"),
    license = "Lesser GPL",
    keywords = "",
    url = "git@bitbucket.org:definex/dsgnutils.git",
    packages=find_packages(),
    long_description=read('README'),
    classifiers=[
    ],
    install_requires=[      #do better...
        'coverage==4.0.3',
        'nose==1.3.7',
        'nose-capturestderr==1.0',
        'psycopg2==2.6.1',
        'pymongo==3.2.2',
        'pytz==2016.4',
        'tzlocal==1.2.2',
    ]
)


