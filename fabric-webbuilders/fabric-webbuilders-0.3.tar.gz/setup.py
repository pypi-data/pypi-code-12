# -*- coding: utf-8 -*-
#
# This file is part of fabric-web-builder (https://github.com/mathiasertl/fabric-web-builder).
#
# fabric-web-builder is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# fabric-web-builder is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with fabric-web-builder.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from setuptools import setup

requires = [
    'GitPython>=1.0.2',
]

setup(
    name='fabric-webbuilders',
    version=str('0.3'),  # py2 requires str not unicode
    description='Build customized and up-to-date versions of HTML/JS/CSS libraries and minify them.',
    author='Mathias Ertl',
    author_email='mati@er.tl',
    platforms='any',
    url='https://github.com/mathiasertl/fabric-webbuilders',
    download_url='https://github.com/mathiasertl/fabric-webbuilders',
    packages=[
        str('fabric_webbuilders'),
    ],
    keywords=[],
    install_requires=requires,
    license="GNU General Public License (GPL) v3",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description="""Fabric tasks to build customized and up-to-date
versions of various popular HTML/Javascript/CSS libraries. Currently supported
are `JQuery <http://jquery.com/>`_ and `Bootstrap
<http://getbootstrap.com/>`_. Additional tasks to minify/concat your JS and CSS files."""
)
