#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='sportsstats',
    version='0.1.3',
    description="Tools for downloading sports statistics.",
    long_description=readme + '\n\n' + history,
    author="William Myers",
    author_email='mwilliammyers+pypi@gmail.com',
    url='https://github.com/mwilliammyers/sportsstats',
    packages=find_packages('lib'),
    package_dir={
        '': 'lib',
    },
    scripts=[
        'bin/stats',
    ],
    include_package_data=True,
    install_requires=[],
    license="GPLv3+",
    zip_safe=False,
    keywords='sportsstats stats statistics sports',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
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
    tests_require=[]
)
