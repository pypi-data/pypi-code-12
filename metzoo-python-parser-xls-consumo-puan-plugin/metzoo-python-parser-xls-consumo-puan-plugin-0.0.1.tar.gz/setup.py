# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

config = {
    'name': 'metzoo-python-parser-xls-consumo-puan-plugin',
    'version': '0.0.1',
    'description': 'Python Puan energy report XLS parser Pluigin for Metzoo',
    'long_description': readme(),
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    'data_files': [
        ('metzoo-python-parser-xls-consumo-puan-plugin/config', ['config-template.yaml'])
    ],
    'keywords': 'metzoo monitoring metric parser',
    'url': 'https://bitbucket.org/edrans/metzoo-python-parser-xls-consumo-puan-plugin',
    'author': 'Edrans',
    'author_email': 'info@edrans.com',
    'license': 'MIT',
    'packages': ['metzoo', 'metzoo.plugins'],
    'install_requires': ['xlrd'],
    'zip_safe': False
}

setup(**config)
