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

requirements = open('requirements.txt').readlines()

test_requirements = open('requirements_dev.txt').readlines()

setup(
    name='reqgen',
    version='0.0.2',
    description='''ReqGen is a requirements generator that searchs recursively in a given
                    path for all requirements.txt and merge them all in a single file with
                    the newest versions found un the files''',
    long_description=readme + '\n\n' + history,
    author='Tulio Ruiz',
    author_email='tulio@vauxoo.com',
    url='https://github.com/ruiztulio/reqgen',
    packages=[
        'reqgen',
    ],
    package_dir={'reqgen':
                 'reqgen'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='reqgen',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
