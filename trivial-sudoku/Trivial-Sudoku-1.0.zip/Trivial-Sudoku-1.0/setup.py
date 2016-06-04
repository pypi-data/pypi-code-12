#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2016 Alexandre Syenchuk (alexpirine)

from setuptools import find_packages, setup

if __name__ == '__main__':
    setup(
        name='Trivial-Sudoku',
        version='1.0',
        url='https://github.com/alexpirine/python-trivial-sudoku',
        license='New BSD License',
        author='Alexandre Syenchuk',
        author_email='as@netica.fr',
        description='A trvial Python implementation of a Sudoku solver',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Education',
            'Topic :: Games/Entertainment :: Puzzle Games',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
