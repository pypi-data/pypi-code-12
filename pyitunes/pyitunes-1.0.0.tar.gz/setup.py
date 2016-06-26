# -*- coding: utf-8 -*-
import itunes
from setuptools import setup

setup(
    name='pyitunes',
    version=itunes.__version__,
    description="A simple python wrapper to access iTunes Store API",
    author='Jonathan Nappi',
    author_email='moogar@comcast.net',
    maintainer='Jonathan Nappi',
    maintainer_email='moogar@comcast.net',
    license='http://www.gnu.org/copyleft/gpl.html',
    platforms=['any'],
    url='https://github.com/moogar0880/python-itunes',
    packages=['itunes'],
)
