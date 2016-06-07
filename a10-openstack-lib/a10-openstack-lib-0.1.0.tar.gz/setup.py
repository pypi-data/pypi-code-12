#!/usr/bin/env python
# flake8: noqa

from setuptools import setup, find_packages
setup(
    name = "a10-openstack-lib",
    version = "0.1.0",
    packages = find_packages(),

    author = "A10 Networks",
    author_email = "dougw@a10networks.com",
    description = "A10 Networks Common OpenStack Library",
    license = "Apache",
    keywords = "a10 adc slb load balancer openstack neutron lbaas cli",
    url = "https://github.com/a10networks/a10-openstack-lib",

    long_description = 'A10 common openstack library',

    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
    ],

    include_package_data=True,

    install_requires = []
)
