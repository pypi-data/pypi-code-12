# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

config = {
    'name': 'metzoo-python-writer',
    'version': '0.0.11',
    'description': 'Python Data Writer for Metzoo',
    'long_description': readme(),
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    'entry_points': {
        'console_scripts': [
            'metzoo-writer = metzoo.writer.writer:main'
        ]
    },
    'data_files': [
        ('metzoo-python-writer/config', ['config-template.yaml'])
    ],
    'keywords': 'metzoo monitoring metric',
    'url': 'https://bitbucket.org/edrans/metzoo-python-writer',
    'author': 'Edrans',
    'author_email': 'info@edrans.com',
    'license': 'MIT',
    'packages': ['metzoo', 'metzoo.writer'],
    'install_requires': ['metzoo-python-lib'],
    'zip_safe': False
}

setup(**config)
