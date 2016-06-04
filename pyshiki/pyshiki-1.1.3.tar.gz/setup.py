#!/usr/bin/env python3
#-*- coding: UTF-8 -*-


'''
@author: OlegWock
@license GNU LESSER GENERAL PUBLIC LICENSE v3, see LICENSE file
Copyright (C) 2016
'''

from distutils.core import setup


setup(
    name='pyshiki',
    version='1.1.3',
    author='OlegWock',
    author_email='olegwock@gmail.com',
    url='https://github.com/OlegWock/PyShiki',
    description='Module for writing scripts for shikimori.org',
    download_url='https://github.com/OlegWock/PyShiki/archive/master.zip',
    license='GNU LESSER GENERAL PUBLIC LICENSE v3, see LICENSE file',

    packages=['pyshiki'],
    install_requires=['requests'],
)