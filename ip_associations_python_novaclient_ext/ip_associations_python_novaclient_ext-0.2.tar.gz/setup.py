# Copyright 2015 Rackspace Hosting Inc.
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

import setuptools

setuptools.setup(
    name='ip_associations_python_novaclient_ext',
    version='0.2',
    description='Adds Rackspace ip_associations support to python-novaclient',
    long_description=open('README.rst').read(),
    author='Rackspace',
    author_email='neutron-requests@lists.rackspace.com',
    url='https://github.com/rackerlabs/ip_associations_python_novaclient_ext',
    license='Apache License, Version 2.0',
    py_modules=['ip_associations_python_novaclient_ext'],
    install_requires=['python-novaclient'],
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
)
