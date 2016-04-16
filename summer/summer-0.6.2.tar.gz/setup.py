# -*- coding: utf-8 -*-
# Time-stamp: < setup.py (2016-04-16 15:56) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from setuptools import setup, find_packages

VERSION = '0.6.2'
DESCRIPTION = """Summer -- light weight Python 3 application framework"""
LONG_DESCRIPTION = """Summer is light weight Python 3 application framework to support some
common tasks in variety of applications. It tries to assist you with
business object management, helps with ORM (mapping, transactions), LDAP,
AOP and localization.  Something like famous Java Spring Framework, but
much more simple."""

CLASSIFIERS = """
Programming Language :: Python :: 3 :: Only
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Development Status :: 4 - Beta
Intended Audience :: Developers
Topic :: Software Development :: Libraries :: Application Frameworks
"""

setup(
    name='summer',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Martin Šlouf',
    author_email='martinslouf@sourceforge.net',
    url='http://py-summer.sourceforge.net/',
    license='Lesser General Public Licence version 3',
    classifiers=[i for i in CLASSIFIERS.split("\n") if i],
    keywords='framework development',
    packages=find_packages(exclude=['tests*']),
    install_requires=['sqlalchemy', 'ldap3'],
    package_data={'summer': ['sample/*.sample']},
)
