import os

import bossformation

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    try:
        import pypandoc
        return pypandoc.convert(source='README.md', to='rst')
    except:
        with open('README.md') as f:
            return f.read()

version = bossformation.__version__

config = {
    'description': 'Tool to enhance AWS CloudFormation',
    'long_description': readme(),
    'author': 'Joseph Wright',
    'url': 'https://github.com/cloudboss/bossformation',
    'download_url': 'https://github.com/cloudboss/bossformation/releases/{}'.format(version),
    'author_email': 'rjosephwright@gmail.com',
    'version': version,
    'install_requires': [
        'boto3',
        'click',
        'jinja2',
        'PyYAML',
    ],
    'packages': ['bossformation'],
    'entry_points': {
        'console_scripts': ['bf = bossformation.cli:main']
    },
    'name': 'bossformation'
}

setup(**config)
