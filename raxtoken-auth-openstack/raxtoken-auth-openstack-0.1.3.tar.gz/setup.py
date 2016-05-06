# Copyright 2016 Russell Troxel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import setuptools
import sys


setuptools.setup(
    name="raxtoken-auth-openstack",
    version="0.1.3",
    author="Russell Troxel",
    author_email="russell.troxel@rackspace.com",
    description="Rackspace Token-Based Auth Plugin for OpenStack Clients.",
    license="Apache License, Version 2.0",
    url="https://github.com/swyytch/raxtoken-auth-openstack",
    download_url = "https://github.com/swyytch/raxtoken-auth-openstack/tarball/0.1.3",
    install_requires=['python-novaclient'],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'test_*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: OpenStack",
        "Programming Language :: Python"
    ],
    entry_points={
        "openstack.client.auth_plugin": [
            "raxtoken = raxtoken_auth_openstack.plugin:RackspaceAuthPlugin"
        ]
    }
)
