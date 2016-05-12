#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

from docuit._version import __version__


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='docuit',
    version=__version__,
    description='Read specific parts from README.md files',
    long_description=long_description,
    author='Tobias Wilken',
    author_email='tooangel@tooangel.de',
    license='AGPL',
    entry_points={
        'console_scripts': [
            'docuit = docuit.__main__:main'
        ]
    },
    packages=find_packages(),
    install_requires=['docopt>=0.6.2'],
    url='https://github.com/TooAngel/docuit'
)
