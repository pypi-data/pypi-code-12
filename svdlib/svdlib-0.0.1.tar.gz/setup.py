# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import svdlib

setup(
    name='svdlib',
    version=svdlib.__version__,
    author=svdlib.__author__,
    author_email=svdlib.__email__,
    description=svdlib.__description__,
    long_description=svdlib.__long_description__,
    url='https://github.com/k0st1an/svdlib',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
