#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from setuptools import setup

version = open('VERSION').read()
readme = open('README').read()
history = open('HISTORY').read().replace('.. :changelog:', '')

# get the requirements from the requirements.txt
requirements_file = open('requirements.txt').read().split()
requirements = requirements_file

# get the test requirements from the test_requirements.txt
test_requirements = []

setup(
    name='RepeaterStatusBot',
    version=version,
    description=(''),
    long_description=readme + '\n\n' + history,
    author='Wim Fournier',
    author_email='wim@fournier.nl',
    url='https://github.com/hsmade/RepeaterScripts/tree/master/RepeaterStatusBot',
    packages=[
        'RepeaterStatusBot',
    ],
    package_dir={'RepeaterStatusBot':
                 '.'},
    include_package_data=True,
    install_requires=requirements,
    license="WTFPL",
    zip_safe=False,
    keywords='RepeaterStatusBot',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
             'RepeaterStatusBot = RepeaterStatusBot:main'
        ]
    },
 
)
