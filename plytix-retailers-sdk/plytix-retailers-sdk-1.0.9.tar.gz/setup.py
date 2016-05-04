# -*- coding: utf-8 -*-

import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('plytix/retailers/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='plytix-retailers-sdk',
    version=version,
    description='Plytix Retailers SDK for Python',
    long_description=open('README.rst').read(),
    author=u'Daniel Sánchez Prolongo',
    author_email='dani@plytix.com',
    url='https://bitbucket.org/plytixdevs/plytix-sdk-python',
    packages=[
        'plytix',
        'plytix.retailers',
        'plytix.retailers.models',
        'plytix.retailers.services'
    ],
    install_requires=[
        'requests>=2.5.3',
    ],
    license='MIT',
    keywords='plytix',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='nose.collector',
    tests_require=[
        'requests>=2.5.3',
        'httpretty',
        'nose',
        'coverage',
        'rednose',
    ],
)
