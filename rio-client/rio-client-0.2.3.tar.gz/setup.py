#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests==2.9.1',
]

test_requirements = [
    'pytest==2.9.1',
    'requests-mock==0.7.0',
]

setup(
    name='rio-client',
    version='0.2.3',
    description="Client for Rio.",
    long_description=readme + '\n\n' + history,
    author="Ju Lin",
    author_email='soasme@gmail.com',
    url='https://github.com/soasme/rio-client',
    packages=find_packages(exclude=('tests', 'tests.*', '*.tests', '*.tests.*', )),
    package_dir={'rio_client': 'rio_client'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='rio',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
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
    tests_require=test_requirements,
)
