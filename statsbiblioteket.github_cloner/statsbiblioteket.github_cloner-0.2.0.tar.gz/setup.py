#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'argparse',
    'typing', # For python 3.4 and older
    'enum34', #For python 3.3 and older
    # TODO: put package requirements here
]

test_requirements = [
    'pytest',
    'pytest-runner',
    # TODO: put package test requirements here
]

setup(
    name='statsbiblioteket.github_cloner',
    version='0.2.0',
    description="Python Command line program for harvesting github "
                "repositories",
    long_description=readme + '\n\n' + history,
    author="Asger Askov Blekinge",
    author_email='asger.askov.blekinge@gmail.com',
    url='https://github.com/blekinge/github_cloner',
    entry_points={
        "console_scripts": ['github_cloner = '
                            'statsbiblioteket.github_cloner.github_cloner'
                            ':main']
    },
    packages=[
        'statsbiblioteket.github_cloner',
    ],
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='github_cloner',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        #"Programming Language :: Python :: 2",
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=['pytest-runner']
)


