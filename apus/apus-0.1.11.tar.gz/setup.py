#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from apus import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'sqlalchemy==1.0.13',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='apus',
    version=__version__,
    description="Caso de estudo para criação de Python Package.",
    long_description=readme + '\n\n' + history,
    author="Geislor Crestani",
    author_email='geislor@gmail.com',
    url='https://github.com/geislor/apus',
    packages=[
        'apus',
        'apus.users',
        'apus.config',
        'apus.fluent_python',
    ],
    package_dir={'apus': 'apus'},
    entry_points={
        'console_scripts': [
            'apus=apus.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='apus',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
