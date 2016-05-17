#!/usr/bin/env python3
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
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='devon',
    version='0.1.1',
    description="Uzbek NLP library",
    long_description=readme + '\n\n' + history,
    author="Sardor Muminov",
    author_email='smuminov@gmail.com',
    url='https://github.com/muminoff/devon',
    packages=[
        'devon',
    ],
    package_dir={'devon':
                 'devon'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='devon',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
