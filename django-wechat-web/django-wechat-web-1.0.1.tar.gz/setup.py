#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : setup.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年04月21日 星期四 16时10分30秒
# *************************************************
import os
from setuptools import find_packages, setup

README = ''
for _file in ('README.rst', 'HISTORY.md'):
    with open(
            os.path.join(
                os.path.dirname(__file__), _file)
            ) as readme:
        README += readme.read()


# allow setup.py to  be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-wechat-web',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to conduct Web-based.',
    long_description=README,
    url='',
    author='Eason Smith',
    author_email='uniquecolesmith@gmail.com',
    install_requires = ['django>=1.9', 'requests'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
