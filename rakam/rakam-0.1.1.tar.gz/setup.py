# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

module_path = os.path.join(os.path.dirname(__file__), 'rakam/__init__.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]


setup(
    name="rakam",
    version=__version__,

    url="https://github.com/kakashit/rakam_client",

    author="Kaan Uğurlu",
    author_email="kugurlu94@gmail.com",

    description="Python client for rakam server.",
    long_description=open('README.rst').read(),

    packages=find_packages(),

    zip_safe=False,
    platforms='any',

    install_requires=[
        'requests>=2.4.3',
        'six>=1.10.0',
        'pytz>=2016.4',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
