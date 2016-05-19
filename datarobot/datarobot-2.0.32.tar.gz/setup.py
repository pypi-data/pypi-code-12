#!/usr/bin/env python
import re

from setuptools import setup

version = ''
with open('datarobot/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='datarobot',
    version=version,
    description='This client library is designed to support the Datarobot '
                'API',
    author='datarobot',
    author_email='support@datarobot.com',
    maintainer='datarobot',
    maintainer_email='info@datarobot.com',
    license='Apache',
    packages=["datarobot",
              "datarobot.models",
              "datarobot.utils",
              "datarobot.helpers",
              "datarobot.ext"],
    long_description="DataRobot Python API",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'requests>=2.8.1,<3.0',
        'python-dateutil>=2.2,<3.0',
        'six>=1.10.0,<2.0',
        'trafaret>=0.7.1,<1.0',
        'pandas>=0.15.2,<1.0',
        'requests_toolbelt>=0.6.0,<1.0'
    ],
)
