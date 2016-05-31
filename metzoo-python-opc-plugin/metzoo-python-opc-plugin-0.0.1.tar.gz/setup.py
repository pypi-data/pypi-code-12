# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

config = {
    'name': 'metzoo-python-opc-plugin',
    'version': '0.0.1',
    'description': 'Python OPC Pluigin for Metzoo',
    'long_description': readme(),
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    'data_files': [
        ('metzoo-python-opc-plugin/config', ['config-template.yaml'])
    ],
    'keywords': 'metzoo monitoring metric opc',
    'url': 'https://bitbucket.org/edrans/metzoo-python-opc-plugin',
    'author': 'Edrans',
    'author_email': 'info@edrans.com',
    'license': 'MIT',
    'packages': ['metzoo', 'metzoo.plugins'],
    'install_requires': ['pyro'],
    'zip_safe': False
}

setup(**config)
