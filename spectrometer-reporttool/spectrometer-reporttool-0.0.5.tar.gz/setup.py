# -*- coding: utf-8 -*-

# @License EPL-1.0 <http://spdx.org/licenses/EPL-1.0>
##############################################################################
# Copyright (c) 2016 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()

setup(
    name='spectrometer-reporttool',
    version='0.0.5',
    author='OpenDaylight Spectrometer Report Tool',
    author_email='spectrometer-dev@lists.opendaylight.org',
    url='https://wiki.opendaylight.org/view/Spectrometer',
    description='',
    long_description=(
        'The main purpose of the spectrometer-reporttool is to generate a '
        'of contributions to OpenDaylight Project by querying the '
        'Spectrometer API server (separate software). '),
    license='EPL',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=install_reqs,
    packages=find_packages(exclude=[
        '*.tests',
        '*.tests.*',
        'tests.*',
        'tests'
    ]),
    entry_points='''
        [console_scripts]
        spectrometer-reporttool=spectrometer.reporttool.cli:cli
    ''',
)
