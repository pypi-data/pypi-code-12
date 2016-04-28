#!/usr/bin/env python3

from setuptools import setup

setup(
        name='tinycm_vim',
        version='0.1.3',
        packages=['tinycm_vim'],
        url='https://github.com/MartijnBraam/TinyCM',
        license='MIT',
        author='Martijn Braam',
        author_email='martijn@brixit.nl',
        description='VIM definition for TinyCM',
        keywords=["configuration management", "puppet"],
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: MIT License"
        ],
        install_requires=[
            'tinycm'
        ]
)
