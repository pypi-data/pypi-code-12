# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014
#
#      Loja Integrada LTDA.  All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#
# in the documentation and/or other materials provided with the distribution.
# * Neither the name of the creators nor the names of its contributors may be used to endorse or promote products derived from
#
# this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE CREATORS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE CREATORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#
##############################################################################

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='li-repo',
    version='1.8.0',
    url='https://github.com/lojaintegrada/LI-Repo',
    license='LIEULA',
    description='Loja Integrada\'s models for Django ORM.',
    author=u'Loja Integrada',
    author_email='contato@lojaintegrada.com.br',
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['distribute', 'Django<1.9', 'jsonfield>=0.9.20', 'psycopg2', 'django-mptt', 'unidecode'],
)
