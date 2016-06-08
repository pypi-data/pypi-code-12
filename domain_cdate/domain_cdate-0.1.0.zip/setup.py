#!/usr/bin/env python
import codecs
import os
import re
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'domain_cdate', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


if sys.version_info < (3, 4, 0):
    raise RuntimeError("aiosocks requires Python 3.4+")


setup(
    name='domain_cdate',
    version='0.1.0',
    packages=['domain_cdate'],
    url='https://github.com/nibrag/domain_cdate',
    license='APACHE 2.0',
    author='Nail Ibragimov',
    author_email='ibragwork@gmail.com',
    description='Domain creation date extractor',
    long_description=open("README.rst").read()
)
