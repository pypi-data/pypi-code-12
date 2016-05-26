#!/usr/bin/env python
#! coding: utf-8

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

setup(
    name='gentletool',
    version='0.1',
    maintainer='Michael Lee',
    maintainer_email='liyong19861014@gmail.com',
    url='https://github.com/airhuman/gentletool',
    description='慢慢删除大文件',
    packages=['gentle'],
    entry_points={
        'console_scripts': [
            'gentle_rm = gentle.rm:main',
        ],
    }
)
