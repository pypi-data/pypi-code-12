#!/usr/bin/env python3

from setuptools import setup

version = '2.0.2'

setup(name='makerestapiclient',
    version=version,
    description="Simple python utility to build a python client class for interfacing with a REST API",
    long_description="Simple python utility to build a python client class for interfacing with a REST API",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    entry_points={
        'console_scripts': [
            'makerestapiclient = makerestapiclient.__main__:main',
            ]
        },
    keywords='python http rest management',
    author='Taylor C. Richberger <tcr@absolute-performance.com>',
    author_email='tcr@absolute-performance.com',
    url='https://github.com/Taywee/makerestapiclient',
    download_url='https://github.com/Taywee/makerestapiclient',
    license='MIT',
    packages=['makerestapiclient'],
    package_data={
        'makerestapiclient': ['templates/*.mustache'],
        },
    install_requires=['setuptools', 'chevron'],
    include_package_data=False,
    zip_safe=False,
    )
