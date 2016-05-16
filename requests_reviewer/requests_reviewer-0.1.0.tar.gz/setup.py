#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests==2.9.1',
]

test_requirements = [
    'mock==2.0.0',
    'requests-mock==0.7.0',
]

setup(
    name='requests_reviewer',
    version='0.1.0',
    description=("Take a HTTP response from requests and adjust the return "
                 "code based on ISP suspension messages, CDN overload messages"
                 " and similar"),
    long_description=readme + '\n\n' + history,
    author="Chris Horsley",
    author_email='chris.horsley@csirtfoundry.com',
    url='https://github.com/chorsley/requests_reviewer',
    packages=[
        'requests_reviewer',
    ],
    package_dir={'requests_reviewer':
                 'requests_reviewer'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='requests_reviewer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
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
