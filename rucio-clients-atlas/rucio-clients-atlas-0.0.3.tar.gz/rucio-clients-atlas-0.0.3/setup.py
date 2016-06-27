# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2016

import glob

from setuptools import setup

setup(
    name='rucio-clients-atlas',
    version='0.0.3',
    data_files=[('rucio/etc/', glob.glob('etc/*.cfg'))],
    include_package_data=True,
    author="Rucio",
    author_email="rucio-dev@cern.ch",
    description="Rucio Client Configuration for ATLAS",
    license="Apache License, Version 2.0",
    url="http://rucio.cern.ch/",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)'],
    install_requires=['rucio-clients>=1.6.0'],
)
