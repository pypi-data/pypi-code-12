#!/usr/bin/env python
# setup.py
# -*- coding: utf-8 -*-
# vim: ai et ts=4 sw=4 sts=4 fenc=UTF-8 ft=python


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'boto',
]

test_requirements = [
    'pytest',
    'tox',
    'responses',
]

setup_requirements = [
    'pytest-runner',
]

setup(
    name='clustercron',
    version='0.4.4',
    description='Cron job wrapper that ensures a script gets run from one node'
    ' in the cluster.',
    long_description=readme + '\n\n' + history,
    author='Maarten Diemel',
    author_email='maarten@maartendiemel.nl',
    url='https://github.com/maartenq/clustercron',
    packages=[
        'clustercron',
    ],
    package_dir={'clustercron': 'clustercron'},
    entry_points={
        'console_scripts': [
            'clustercron = clustercron.main:command',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    keywords='clustercron',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
