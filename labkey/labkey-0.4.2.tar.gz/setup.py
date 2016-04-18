#
# Copyright (c) 2015-2016 LabKey Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Setup script for Python client API for LabKey Server.

Also installs included versions of third party libraries, if those libraries
are not already installed.
"""
from setuptools import setup

packages = [
    'labkey'
]

long_desc = "Python client API for LabKey Server. Supports query and experiment APIs."

setup(
    name='labkey',
    version='0.4.2',
    description='Python client API for LabKey Server',
    long_description=long_desc,
    license="Apache License 2.0",
    author='LabKey Software',
    author_email='nicka@labkey.com',
    maintainer='Nick Arnold',
    maintainer_email='nicka@labkey.com',
    url='https://github.com/LabKey/labkey-api-python',
    packages=packages,
    package_data={},
    install_requires=['requests'],
    tests_require=['requests', 'mock'],
    keywords="labkey api client",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering'
    ]
)
