#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PYTHON3 = sys.version_info[0] > 2

required = [
    'requests>=2.9',
    'websocket-client==0.35.0',
    'beautifulsoup4==4.4.1',
    'html5lib==0.9999999',
    'pyfiglet==0.7.4',
    'slackrtm==0.2.1',
    'certifi==2015.04.28'
]
if not PYTHON3:
    required += ['importlib>=1.0.3']

packages = ['limbo', 'limbo.plugins']

try:
    longdesc = open("README.rs").read()
except:
    longdesc = ''

setup(
    name='dlbot',
    version='0.0.2',
    description='Simple and Clean Slack Chatbot',
    long_description=longdesc,
    author='Dataloop',
    author_email='info@dataloop.io',
    url='https://github.com/dataloop/dlbot',
    packages=packages,
    scripts=['bin/dlbot'],
    package_data={'': ['LICENSE',], '': ['limbo/plugins/*.py']},
    exclude_package_data={'': ['run_bot.sh']},
    include_package_data=True,
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ),
)
