#!/usr/bin/env python3

from setuptools import setup, find_packages

version = '0.1.0'

with open('README.rst') as readme:
    description = readme.read() + "\n\n"

requires = ['Sphinx>=1.4']

setup(
    author="Jan Dittberner",
    author_email="jan@dittberner.info",
    description="MAC address extension for Sphinx",
    long_description=description,
    install_requires=requires,
    keywords="sphinx extension MAC",
    name="jandd.sphinxext.mac",
    namespace_packages=['jandd', 'jandd.sphinxext'],
    packages=find_packages(),
    platforms='any',
    version=version,
    license="GPLv3+",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Sphinx :: Extension",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Internet",
    ]
)
