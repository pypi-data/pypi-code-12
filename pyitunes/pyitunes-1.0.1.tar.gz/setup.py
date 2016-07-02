# -*- coding: utf-8 -*-
import itunes
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()
with open('requirements.txt') as f:
    requires = [line.strip() for line in f if line.strip()]

setup(
    name='pyitunes',
    version=itunes.__version__,
    description="A simple python wrapper to access iTunes Store API",
    long_description=readme,
    author='Jonathan Nappi',
    author_email='moogar@comcast.net',
    maintainer='Jonathan Nappi',
    maintainer_email='moogar@comcast.net',
    license='http://www.gnu.org/copyleft/gpl.html',
    platforms=['any'],
    url='https://github.com/moogar0880/python-itunes',
    packages=['itunes'],
    install_requires=requires,
    zip_safe=False,
)
