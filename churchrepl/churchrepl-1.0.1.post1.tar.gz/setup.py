#!/usr/bin/env python
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    url='https://github.com/CodeGrimoire/ChurchREPL',
    name='churchrepl',
    version='1.0.1-post1',
    description='A simple REPL for lambda calculus',
    long_description=long_description,
    author='Luke Smith',
    author_email='lsmith@zenoscave.com',
    license='BSD',
    entry_points={'console_scripts': [
        'churchrepl = churchrepl.__main__:main',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows :: Windows 7',
    ],
    packages=['churchrepl', 'churchrepl.repl'],
    install_requires=['grako', 'future'],
)
