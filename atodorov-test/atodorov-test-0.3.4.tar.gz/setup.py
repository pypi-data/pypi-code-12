#!/usr/bin/env python

from setuptools import setup, find_packages

config = {
    'name' : 'atodorov-test',
    'version' : '0.3.4',
    'packages' : find_packages(),
    'author' : 'Alexander Todorov',
    'author_email' : 'atodorov@nopam.otb.bg',
    'license' : 'BSD',
    "description" : 'Dummy test package, please ignore.',
    'long_description' : 'Test package',
    'url' : 'https://github.com/atodorov/bztest',
}

setup(**config)
