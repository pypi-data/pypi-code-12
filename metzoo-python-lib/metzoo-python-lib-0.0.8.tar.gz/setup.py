# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

config = {
    'name': 'metzoo-python-lib',
    'version': '0.0.8',
    'description': 'Python Database Library for Metzoo',
    'long_description': readme(),
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    'keywords': 'metzoo monitoring metric',
    'url': 'https://bitbucket.org/edrans/metzoo-python-lib',
    'author': 'Edrans',
    'author_email': 'info@edrans.com',
    'license': 'MIT',
    'packages': ['metzoo', 'metzoo.lib'],
    'install_requires': [],
    'zip_safe': False
}

setup(**config)

