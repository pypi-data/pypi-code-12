#-*- coding: utf-8 -*-
__author__ = 'tangke'
import codecs
import os
import sys

try:
    from setuptools import setup,find_packages
except:
    from distutils.core import setup,find_packages
setup(
    name = "MosT",
    version = "0.12",
    description = "auto test with interface",
    long_description = "",
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = "auto test",
    author = "tangke",
    author_email = "243556090@qq.com",
    url = "",
    license = "",
    packages = find_packages(),
    include_package_data=True,
    zip_safe=True,
)