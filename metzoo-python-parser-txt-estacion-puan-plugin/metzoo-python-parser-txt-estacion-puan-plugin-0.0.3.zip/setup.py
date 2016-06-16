# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

config = {
    'name': 'metzoo-python-parser-txt-estacion-puan-plugin',
    'version': '0.0.3',
    'description': 'Puan meteorology station TXT parser Pluigin for Metzoo',
    'long_description': readme(),
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    'data_files': [
        ('metzoo-python-parser-txt-estacion-puan-plugin/config', ['config-template.yaml'])
    ],
    'keywords': 'metzoo monitoring metric parser',
    'url': 'https://bitbucket.org/edrans/metzoo-python-parser-txt-estacion-puan-plugin',
    'author': 'Edrans',
    'author_email': 'info@edrans.com',
    'license': 'MIT',
    'packages': ['metzoo', 'metzoo.plugins'],
    'install_requires': [],
    'zip_safe': False
}

setup(**config)
