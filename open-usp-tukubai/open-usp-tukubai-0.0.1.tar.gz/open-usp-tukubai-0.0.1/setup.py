#!/usr/bin/env python

from setuptools import setup

version = '0.0.1'
name = 'open-usp-tukubai'
short_description = '`open-usp-tukubai` is a command set for shell scripting.'
long_description = """\
`open-usp-tukubai` is a command set for shell scripting.

Setup
-----
::

   $ pip install open-usp-tukubai

History
-------
0.0.1 (2016-05-27)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 4 - Beta",
   "Environment :: Console",
   "License :: OSI Approved :: MIT License",
   "Programming Language :: Python",
   "Topic :: Utilities",
]

commands = [
    'calclock',
    'cgi-name',
    'check_attr_name',
    'check_need_name',
    'cjoin0',
    'cjoin1',
    'cjoin2',
    'comma',
    'count',
    'ctail',
    'dayslash',
    'delf',
    'divsen',
    'filehame',
    'formhame',
    'getfirst',
    'getlast',
    'gyo',
    'han',
    'join0',
    'join1',
    'join2',
    'juni',
    'kasan',
    'keta',
    'keycut',
    'loopj',
    'loopx',
    'maezero',
    'map',
    'marume',
    'mdate',
    'mime-read',
    'mojihame',
    'nameread',
    'numchar',
    'plus',
    'rank',
    'ratio',
    'retu',
    'self',
    'sm2',
    'sm4',
    'sm5',
    'tarr',
    'tateyoko',
    'tcat',
    'unmap',
    'up3',
    'yarr',
    'ycat',
    'yobi',
    'ysum',
    'zen',
]
scripts = [ 'COMMANDS/%s' % c for c in commands ]
setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    url='https://github.com/usp-engineers-community/Open-usp-Tukubai',
    license='MIT',
    scripts=scripts,
)


