# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description
__author__ = 'themanda'
__version__ = '0.1.0'
import os
from distutils.core import setup
try:
    from setup_tools import find_packages
except ImportError:
    def find_packages():
        """When setup_tools find_packages fail because are not installed or some similar behavior
        this overwrite it and return default package.
        :return: list
        """
        return ['ng_factory']


def read(f):
    """ Read a file and get string from it
    :param f: file to read
    :return: file content as string
    """
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(
    name='ng_factory',
    version=__version__,
    description='Instrospective Factory pattern library',
    long_description=read('README.rst'),
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    author='Jorge A. Medina',
    author_email='j@engine.cl',
    url='http://github.com/engine-cl/ng-factory',
    packages=find_packages(),
    license='BSD',
    keywords=['factory', 'introspective']
)
