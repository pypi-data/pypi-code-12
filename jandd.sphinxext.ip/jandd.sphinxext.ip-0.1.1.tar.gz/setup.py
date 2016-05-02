#!/usr/bin/env python3

from setuptools import setup, find_packages

version = '0.1.1'

with open('README.rst') as readme:
    description = readme.read() + "\n\n"

with open('COPYING') as license:
    description += license.read()

requires = ['Sphinx>=1.4', 'ipcalc>=1.99']
tests_requires = ['path.py>=8.2.1']


setup(
    author="Jan Dittberner",
    author_email="jan@dittberner.info",
    description="IP address extensions for Sphinx",
    long_description=description,
    include_package_data=True,
    install_requires=requires,
    keywords="sphinx extension IP",
    license="GPLv3+",
    name="jandd.sphinxext.ip",
    namespace_packages=['jandd', 'jandd.sphinxext'],
    packages=find_packages(),
    platforms='any',
    tests_requires=tests_requires,
    version=version,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Sphinx :: Extension",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Internet",
    ],
)
