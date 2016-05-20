#/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit

try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools.")

from os.path import exists

description = 'Utils for ryoka'
long_description = "%s" % (description)
readme_path = "README.txt"
version = ""

if exists(readme_path):
    for line in open(readme_path, "r"):
        long_description = "%s\n%s" % (long_description, line)
    readme = open(readme_path, "r")
    readme_one_line = readme.readline()
    version = readme_one_line.split(' ')[1].strip()
    readme.close()

if (version == ""):
    print("Not found version in %s" % (readme_path))
    exit()

setup(
    name  = 'ryoka_utils',
    version = version,
    description = description,
    long_description = long_description,
    license = 'MIT',
    author = 'Ryoya Kamikawa',
    author_email = 'ry_1324@yahoo.co.jp',
    url = 'https://ryoka419319@bitbucket.org/ryoka419319/ryoka_utils.git',
    keywords = 'ryoka utils',
    packages = find_packages(),
    install_requires = [],
)
