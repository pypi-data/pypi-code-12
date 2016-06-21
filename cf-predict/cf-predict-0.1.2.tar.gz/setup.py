#!/usr/bin/env python

"""Setup script for cf-predict."""

import setuptools

from cf_predict import __project__, __version__

try:
    README = open("README.rst").read()
    CHANGES = open("CHANGES.rst").read()
except IOError:
    DESCRIPTION = "<placeholder>"
else:
    DESCRIPTION = README + '\n' + CHANGES

setuptools.setup(
    name=__project__,
    version=__version__,

    description="Cloud Foundry Python Predictive API Boilerplate",
    url='https://github.com/ronert/cf-predict',
    author='Ronert Obst',
    author_email='ronert.obst@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=(DESCRIPTION),
    license='MIT',
    classifiers=[
        # TODO: update this list to match your application: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    install_requires=open("requirements.txt").readlines(),
)
